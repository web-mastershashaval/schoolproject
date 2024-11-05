from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.


class Lawyer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, default='+254 ', help_text='Enter phone number in the format: +254XXXXXXXXX')
    specialties = models.CharField(max_length=100, help_text='List your specialties, e.g., Family Law, Criminal Defense.')
    cases = models.TextField(blank=True, null=True, help_text='Describe cases you have handled or are currently handling.')
    bio = models.TextField(max_length=255, default='sheria ni msumeno ukatao kuwili', help_text='A brief bio of the lawyer.')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.license_number}"

    class Meta:
        verbose_name = "Lawyer"
        verbose_name_plural = "Lawyers"
        
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

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_appointments')
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='lawyer_appointments')
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    appointment_date = models.DateTimeField(default=timezone.now)
    day_time = models.CharField(max_length=10, choices=DAY_TIME_CHOICES)
    best_way = models.CharField(max_length=20, choices=BEST_WAY_CHOICES)
    state_problem = models.TextField()
    additional_text = models.TextField()

    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name} - {self.appointment_date}"


class CaseManagement(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_cases')
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='lawyer_cases')
    case_title = models.CharField(max_length=30)
    date = models.DateField(default=timezone.now)
    case_description = models.TextField(default="state your case here ...")

    def __str__(self):
        return self.case_title

class UploadFiles(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_uploads') 
    file = models.FileField(upload_to='uploads/')
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded at {self.upload_time}"

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lawyer_payments') 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"