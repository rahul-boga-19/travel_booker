from django.urls import path
from user import views



urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('travels/', views.travel_list, name='travel_list'),
    path('travel/<int:pk>/', views.travel_detail, name='travel_detail'),
    path('book/<int:pk>/', views.book_travel, name='book_travel'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
]
