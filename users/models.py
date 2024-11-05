from django.db import models
from django.conf import settings  # Import settings to access the user model
from django.utils import timezone
from django.contrib.auth.models import User
from lawyers.models import Lawyer

class Appointment(models.Model):
    BEST_WAY_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('in_person', 'In Person'),
    ]
    DAY_TIME_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_appointments')  # Use the built-in user model
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    appointment_date = models.DateTimeField(default=timezone.now)
    day_time = models.CharField(max_length=10, choices=DAY_TIME_CHOICES)
    best_way = models.CharField(max_length=20, choices=BEST_WAY_CHOICES)
    state_problem = models.TextField()
    additional_text = models.TextField()

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.appointment_date}"

class Profile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profiles')
    first_name = models.CharField(max_length=30, null=True)  # Allow null
    last_name = models.CharField(max_length=30, null=True)  # Allow null
    email = models.EmailField()  # Consider making this unique
    county = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    postaddress = models.CharField(max_length=30)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)  # Optional
    about = models.TextField(blank=True, null=True)  # Allow blank and null
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Profile picture field

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"

class CaseManagement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cases')
    client_name = models.CharField(max_length=20,null=True)
    case_title = models.CharField(max_length=30)
    date = models.DateField(default=timezone.now)
    case_description = models.TextField(default="state your case here ...")
    document = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return self.case_title

class UploadFiles(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded at {self.upload_time}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  # Keep this to set the timestamp when created
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"
    
class Client(models.Model):  # Assuming this is your customer model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    selected_lawyer = models.ForeignKey(Lawyer, on_delete=models.SET_NULL, null=True, related_name='clients')

    def __str__(self):
        return self.user.username    
