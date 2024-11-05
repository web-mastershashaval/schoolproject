from django import forms
from .models import Lawyer,Appointment,CaseManagement,UploadFiles,Payment,Message
from users.models import Client

class LawyerAdminForm(forms.ModelForm):
    class Meta:
        model = Lawyer
        fields = ['user', 'license_number','phone', 'specialties','bio','profile_picture']

class LawyerProfileForm(forms.ModelForm):
    class Meta:
        model = Lawyer
        fields = ['license_number', 'phone','specialties', 'bio', 'profile_picture']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['client', 'phone_number', 'email', 'appointment_date', 'day_time', 'best_way', 'state_problem', 'additional_text']

class CaseForm(forms.ModelForm):
    class Meta:
        model = CaseManagement
        fields = ['client', 'case_title', 'case_description']

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFiles
        fields = ['file']           


class PaymentForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=Client.objects.all(),  # This queryset gets all clients
        label="Select Client",
        to_field_name='user'  # Use 'user' to refer to the User field in Client
    )

    class Meta:
        model = Payment
        fields = ['user', 'amount', 'status']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']

    def __init__(self, *args, **kwargs):
        self.receiver = kwargs.pop('receiver', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.initial['sender']  # Set sender from initial data
        message.receiver = self.receiver  # Set the receiver
        if commit:
            message.save()
        return message