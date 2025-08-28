from django.db import models
from django.contrib.auth.models import User

class TravelOption(models.Model):
    TYPE_CHOICES = [
        ('Flight','Flight'),
        ('Train','Train'),
        ('Bus','Bus'),
    ]


    travel_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return f" {self.travel_type}: {self.source} -> {self.destination}"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed','Confirmed'),
        ('Cancelled','Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE)
    num_seats = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    def __str__(self):
        return f"{self.id} - {self.user.username} - {self.status}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
