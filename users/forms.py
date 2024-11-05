from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import *
User = get_user_model()
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})  # Add the CSS class

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['phone_number', 'email', 'appointment_date', 'day_time', 'best_way', 'state_problem', 'additional_text']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        lawyer = cleaned_data.get('lawyer')

        # Ensure the user has selected a lawyer before booking an appointment
        # if not LawyerSelection.objects.filter(user=self.user).exists():
        #     raise forms.ValidationError("You must select a lawyer before booking an appointment.")

        return cleaned_data
    
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'county', 'postaddress', 'about','profile_picture']

class CaseManagementForm(forms.ModelForm):
    class Meta:
        model = CaseManagement
        fields = [ 'client_name', 'case_title', 'date', 'case_description','document']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Ensure the user has selected a lawyer before filing a case
        # if not LawyerSelection.objects.filter(user=self.user).exists():
        #     raise forms.ValidationError("You must select a lawyer before filing a case.")

        return cleaned_data

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadFiles
        fields = ['file']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Ensure the user has selected a lawyer before uploading files
        # if not LawyerSelection.objects.filter(user=self.user).exists():
        #     raise forms.ValidationError("You must select a lawyer before uploading files.")

        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [ 'amount']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Ensure the user has selected a lawyer before making a payment
        # if not LawyerSelection.objects.filter(user=self.user).exists():
        #     raise forms.ValidationError("You must select a lawyer before making a payment.")

        return cleaned_data

    def save(self, commit=True):
        payment = super().save(commit=False)
        payment.user = self.user  # Set the user on the payment
        if commit:
            payment.save()
        return payment

