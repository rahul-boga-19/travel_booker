from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import TravelOption, Booking, Profile
from django.contrib.auth.models import User

from django.db import transaction

def index(request):
    latest = TravelOption.objects.order_by('datetime')[:5]
    return render(request, 'user/index.html', {'latest': latest})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()

        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        phone=request.POST['phone']
        address=request.POST['address']
        if not username or not email or not password:
            messages.error(request, "Please fill all required fields.")
            return redirect('register')
        if password != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user,address=address,phone=phone)

        login(request, user)
        messages.success(request, f"Welcome {username}, registration successful.")
        return redirect('index')

    return render(request, 'user/register.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('/admin')
            else:
                login(request, user)
                return redirect('index')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    return render(request, 'user/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
    user = request.user
    if user.is_superuser:
        return redirect('/admin') 
    profile, created = Profile.objects.get_or_create(user=user)


    context = { 
        'user': user,
        'profile': profile
    }

 
  
    return render(request, 'user/profile.html', context)

    

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile
@login_required
def update_profile(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        address = request.POST.get("address")
        phone = request.POST.get("phone")

        # ✅ check username duplication (exclude current user)
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, "Username already exists")
            return redirect("update_profile")

        # ✅ check email duplication (optional)
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, "Email already exists")
            return redirect("update_profile")

        # update user
        user.username = username
        user.email = email
        user.save()

        # update profile
        if profile:  # ensure profile exists
            profile.address = address
            profile.phone = phone
            profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile") 

    context = {
        "user_obj": user,
        "profile": profile
    }
    return render(request, "user/update_profile.html", context)



def travel_list(request):
    travels = TravelOption.objects.all().order_by('datetime')
    q_type = request.GET.get('type','')
    q_source = request.GET.get('source','')
    q_dest = request.GET.get('destination','')
    q_date = request.GET.get('date','')

    if q_type:
        travels = travels.filter(travel_type__iexact=q_type)
    if q_source:
        travels = travels.filter(source__icontains=q_source)
    if q_dest:
        travels = travels.filter(destination__icontains=q_dest)
    if q_date:
        # expect yyyy-mm-dd
        try:
            from datetime import datetime
            date_obj = datetime.strptime(q_date, '%Y-%m-%d').date()
            travels = travels.filter(datetime__date=date_obj)
        except Exception:
            messages.warning(request, "Date format should be YYYY-MM-DD.")

    return render(request, 'user/travel_list.html', {'travels': travels})

def travel_detail(request, pk):
    travel = get_object_or_404(TravelOption, pk=pk)
    return render(request, 'user/travel_detail.html', {'travel': travel})

@login_required
@transaction.atomic
def book_travel(request, pk):
    travel = get_object_or_404(TravelOption, pk=pk)
    if request.method == 'POST':
        try:
            num_seats = int(request.POST.get('num_seats', '1'))
        except ValueError:
            messages.error(request, "Seats must be a number.")
            return redirect('travel_detail', pk=pk)

        if num_seats <= 0:
            messages.error(request, "Number of seats must be at least 1.")
            return redirect('travel_detail', pk=pk)


        if num_seats > travel.available_seats:
            messages.error(request, f"Only {travel.available_seats} seats available.")
            return redirect('travel_detail', pk=pk)

    
        total_price = travel.price * num_seats

        booking = Booking.objects.create(
     
            user=request.user,
            travel_option=travel,
            num_seats=num_seats,
            total_price=total_price,
            status='Confirmed'
        )

        # reduce available seats
        travel.available_seats -= num_seats
        travel.save()

        return render(request, 'user/booking_success.html', {'booking': booking})
    # GET: show booking form on travel detail
    return redirect('travel_detail', pk=pk)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'user/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status == 'Cancelled':
        messages.info(request, "Booking already cancelled.")
        return redirect('my_bookings')

    # restore seats
    travel = booking.travel_option
    travel.available_seats += booking.num_seats
    travel.save()

    booking.status = 'Cancelled'
    booking.save()
    messages.success(request, "Booking cancelled.")
    return redirect('my_bookings')

