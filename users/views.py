from django.shortcuts import render, redirect,get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, AppointmentForm, CaseManagementForm, UploadFileForm, PaymentForm
from .models import Profile,Payment,CaseManagement,Client,Appointment,UploadFiles

from lawyers.models import Message
from lawyers.forms import MessageForm


from lawyers.models import UploadFiles as LawyerUploadFiles
from users.models import UploadFiles as ClientUploadFiles


from django.contrib.auth.models import Group
from django.http import JsonResponse
from lawyers.models import Lawyer
from .decorator import lawyer_selected_required
import calendar
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from .antilawyer import client_required
from datetime import timedelta
from django.db.models import Q

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            client_group = Group.objects.get(name='Clients')
            client_group.user_set.add(user)  # Add the user to the Clients group
            
            # Create a profile for the new user
            Profile.objects.get_or_create(user=user)  # Ensure a profile exists
            
            # Create a Client instance for the new user
            Client.objects.create(user=user)  # Ensure a client instance is created

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('signin')  # Redirect to the user dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/sign-up.html', {'form': form})

import logging

logger = logging.getLogger(__name__)

def signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful.')

                # Check user groups instead of attributes
                if user.groups.filter(name='Lawyers').exists():
                    return redirect('lawyers:lawyer_dashboard')  # Redirect to lawyer dashboard
                elif user.groups.filter(name='Clients').exists():
                    return redirect('users:dashboard')  # Redirect to client dashboard
                else:
                    messages.warning(request, 'Please complete your profile.')
                    return redirect('users:profile_management_view')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'users/sign-in.html', {'form': form})



def home(request):
    return render(request, 'index.html')

def user_category_view(request):
    return render(request, 'users/usercategory.html')

@login_required
@client_required
def dashboard_view(request):
    appointment_form = AppointmentForm()
    profile_form = ProfileForm()
    casemanagement_form = CaseManagementForm()
    upload_file_form = UploadFileForm()
    payment_form = PaymentForm()

    if request.method == 'POST':
        if request.user.groups.filter(name='Lawyers').exists():
        # Logic for lawyers
            return render(request, 'lawyers/dashboard.html')  # Render lawyer's dashboard
        elif request.user.groups.filter(name='Clients').exists():
                # Logic for clients
            return render(request, 'clients/dashboard.html')  # Render client's dashboard
       
        elif 'home' in request.POST:
            return render(request, 'users/home.html')
        elif 'appointment' in request.POST:
            appointment_form = handle_appointment_form(request)
        elif 'profile_management' in request.POST:
            profile_form = handle_profile_form(request)
        elif 'casemanagement' in request.POST:
            casemanagement_form = handle_case_management_form(request)
        elif 'upload_files' in request.POST:
            upload_file_form = handle_upload_file_form(request)
        elif 'payment' in request.POST:
            payment_form = handle_payment_form(request)
        elif 'Lawyers' in request.POST:
            return redirect('users:lawyers_list')  # Redirect to the lawyers list page

        return redirect('users:dashboard')

    return render(request, 'dashboard.html', {
        'user': request.user,
        'appointment_form': appointment_form,
        'profile_form': profile_form,
        'casemanagement_form': casemanagement_form,
        'upload_file_form': upload_file_form,
        'payment_form': payment_form,
    })


@client_required
@login_required
def home_dashboard_view(request):
    now = timezone.now()
    appointments = request.user.client_appointments.all()

    has_upcoming_appointments = appointments.filter(appointment_date__gt=now).exists()
     # Get or create the user's profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Check for unread messages
    unread_messages_count = Message.objects.filter(receiver=request.user, is_read=False).count()
    has_unread_messages = unread_messages_count > 0

    # Generate a monthly calendar
    year = now.year
    month = now.month
    cal = calendar.monthcalendar(year, month)
    calendar_days = []

    for week in cal:
        week_days = []
        for day in week:
            if day != 0:
                date = datetime(year, month, day)
                week_days.append({
                    'day': day,
                    'date': date,
                })
            else:
                week_days.append({
                    'day': '',
                    'date': None,
                })
        calendar_days.append(week_days)

    return render(request, 'users/home.html', {
        'has_upcoming_appointments': has_upcoming_appointments,
        'has_unread_messages': has_unread_messages,
        'calendar': calendar_days,
        'appointments': appointments,
        'profile': profile,
    })


def handle_appointment_form(request):
    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.user = request.user
        appointment.save()
        messages.success(request, 'Appointment scheduled successfully!')
    else:
        messages.error(request, 'There was an error with your appointment form.')
    return form

def handle_profile_form(request):
    form = ProfileForm(request.POST)
    if form.is_valid():
        profile, created = Profile.objects.get_or_create(user=request.user)
        for field in form.cleaned_data:
            setattr(profile, field, form.cleaned_data[field])
        profile.save()
        messages.success(request, 'Profile updated successfully!')
    else:
        messages.error(request, 'There was an error updating your profile.')
    return form

@login_required
@client_required
def create_profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()

            messages.success(request, 'Profile created successfully!')
            return redirect('users:profile_management_view') 

    else:
        form = ProfileForm()

    return render(request, 'users/create_profile.html', {'form': form})

@login_required
def profile_management_view(request):
    # Get or create the profile for the current user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Include request.FILES to handle file uploads
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save the profile instance
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile_management_view')  
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/profile_form.html', {'form': form, 'profile': profile})


def handle_case_management_form(request):
    form = CaseManagementForm(request.POST)
    if form.is_valid():
        case = form.save(commit=False)
        case.user = request.user
        case.save()
        messages.success(request, 'Case saved successfully!')
    return form

@login_required
@client_required
@lawyer_selected_required
def case_management_view(request):
    if request.method == 'POST':
        form = CaseManagementForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            case = form.save(commit=False)
            case.user = request.user  # Ensure the user is set
            case.save()  # Save the case, which includes the document
            messages.success(request, 'Case saved successfully!')
            return redirect('users:casemanagement')
    else:
        form = CaseManagementForm(user=request.user)  # Pass user in GET request as well

    return render(request, 'users/casemanagement_form.html', {'form': form})


def handle_upload_file_form(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = form.save(commit=False)
        uploaded_file.user = request.user
        uploaded_file.save()
        messages.success(request, 'File uploaded successfully!')
    else:
        messages.error(request, 'There was an error uploading your file.')
    return form

def logout_view(request):
    logout(request)
    return redirect('users:sign-in')

@login_required
@client_required
@lawyer_selected_required
def create_appointment(request):
    today = timezone.now()  # Get current datetime
    max_date = today + timedelta(days=5 * 30)  # Five months ahead

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment_datetime = form.cleaned_data['appointment_date']  # This should be a datetime object
            
            # Validate the appointment date
            if appointment_datetime < today:
                messages.error(request, "You cannot schedule an appointment for a past date.")
            elif appointment_datetime > max_date:
                messages.error(request, "You cannot schedule an appointment more than 5 months in advance.")
            else:
                appointment = form.save(commit=False)
                appointment.user = request.user
                appointment.save()
                messages.success(request, "Appointment booked successfully!")
                return redirect('users:appointment_confirmation')  # Redirect to a confirmation page

        else:
            messages.error(request, "There was an error with your appointment form.")
    else:
        form = AppointmentForm()

    return render(request, 'users/appointment_form.html', {
        'form': form,
        'today': today,
        'max_date': max_date,
    })

def appointment_confirmation(request):
    return render(request,'users/appointment_success.html')

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully!")
            return redirect('users:manage_appointments')
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'users/appointment_form.html', {'form': form})


@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment canceled successfully!")
        return redirect('users:manage_appointments')

    return render(request, 'users/confirm_delete.html', {'appointment': appointment})

@login_required
def manage_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'users/manage_appointments.html', {'appointments': appointments})


@login_required
@client_required
@lawyer_selected_required
def payment_view(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment = Payment.objects.create(user=request.user, amount=amount, status='completed')
            messages.success(request, "Payment successful!")
            return redirect('users:payment_success')
    else:
        form = PaymentForm()

    return render(request, 'users/payment.html', {'form': form})

def payment_success_view(request):
    return render(request, 'users/payment_success.html')

def handle_payment_form(request):
    form = PaymentForm(request.POST)
    if form.is_valid():
        payment_form = form.save(commit=False)
        payment_form.user = request.user
        payment_form.save()
        messages.success(request, 'Payment made successfully!')
    else:
        messages.error(request, 'There was an error while making payments.')
    return form

@login_required
@client_required
@lawyer_selected_required
def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)  # Handle file uploads
        if form.is_valid():
            upload_file = form.save(commit=False)  # Don't save yet
            upload_file.user = request.user  # Associate the uploaded file with the logged-in user
            upload_file.save()  # Save the file to the database
            messages.success(request, 'File uploaded successfully!')
            return redirect('users:upload_files')  # Redirect to view files page
    else:
        form = UploadFileForm()

    return render(request, 'users/upload_file_form.html', {'form': form})


@login_required
@client_required
@lawyer_selected_required
def client_files_view(request):
    lawyer_files = LawyerUploadFiles.objects.filter(user=request.user)

    # Fetch client's uploaded files associated with the logged-in lawyer
    client_files = ClientUploadFiles.objects.filter(user__client__selected_lawyer=request.user.lawyer)


    return render(request, 'users/upload_file_form.html', {
        'client_files': client_files,
        'lawyer_files': lawyer_files,
    })





@login_required
@lawyer_selected_required
def delete_document(request, document_id):
    case = get_object_or_404(CaseManagement, id=document_id, user=request.user)
    if request.method == 'POST':
        case.document.delete()  # Delete the file from storage
        case.document = None     # Remove the reference from the model
        case.save()
        messages.success(request, "Document deleted successfully.")
        return redirect('documents_view')  # Redirect to your documents view
    else:
        messages.error(request, "Error deleting document.")
        return redirect('documents_view')


@login_required
@lawyer_selected_required
def documents_view(request):
    cases = CaseManagement.objects.filter(user=request.user)
    return render(request, 'users/documents.html', {'cases': cases})

@login_required
@client_required
def select_lawyer(request, lawyer_id):
    if request.method == 'POST':
        if request.user.groups.filter(name='Clients').exists():
            # Store the selected lawyer ID in the session
            request.session['selected_lawyer'] = lawyer_id
            return JsonResponse({'message': 'Lawyer selected successfully.'})
        else:
            return JsonResponse({'error': 'Unauthorized action.'}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@client_required
def choose_lawyer(request):
    # Get the lawyers available for selection
    lawyers = Lawyer.objects.all()
    
    # Check if a Client instance exists for the logged-in user
    client = get_object_or_404(Client, user=request.user)

    # If the user has selected a lawyer, fetch that info
    selected_lawyer_id = request.session.get('selected_lawyer')
    if selected_lawyer_id:
        selected_lawyer = get_object_or_404(Lawyer, id=selected_lawyer_id)
    else:
         selected_lawyer = client.selected_lawyer

    if request.method == 'POST':
        selected_lawyer_id = request.POST.get('lawyer')
        selected_lawyer = get_object_or_404(Lawyer, id=selected_lawyer_id)
        client.selected_lawyer = selected_lawyer
        client.save()
        # Store in session for consistency
        request.session['selected_lawyer'] = selected_lawyer_id
        return redirect('users:lawyer_profile', lawyer_id=selected_lawyer_id)

    return render(request, 'users/choose_lawyer.html', {
        'lawyers': lawyers,
        'selected_lawyer': selected_lawyer,
    })

@login_required
@lawyer_selected_required
def lawyer_profile_view(request, lawyer_id):
    lawyer = get_object_or_404(Lawyer, id=lawyer_id)
    
    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {
            'name': lawyer.user.first_name + " " + lawyer.user.last_name,
            'specialty': lawyer.specialties,  # Assuming 'specialties' is a field in Lawyer
            'email': lawyer.user.email,
            'phone_number': lawyer.phone_number,
            'bio': lawyer.bio,
        }
        return JsonResponse(data)
    
    # If it's a regular request, render the profile page
    clients = lawyer.clients.all()  # Get all clients who selected this lawyer
    return render(request, 'users/lawyer_profile.html', {'lawyer': lawyer, 'clients': clients})


@login_required
@client_required
def client_message_view(request):
    client = request.user.client
    selected_lawyer = client.selected_lawyer
    messages_list = []

    if selected_lawyer:
        messages_list = Message.objects.filter(
            (Q(sender=client.user) & Q(receiver=selected_lawyer.user)) | 
            (Q(sender=selected_lawyer.user) & Q(receiver=client.user))
        ).order_by('-timestamp')

    if request.method == 'POST':
        # Handle message deletion
        if 'delete_messages' in request.POST:
            message_ids = request.POST.getlist('message_ids')  # Get list of selected message IDs
            if message_ids:  # Check if any IDs were selected
                Message.objects.filter(id__in=message_ids).delete()  # Delete messages
                messages.success(request, 'Selected messages deleted successfully!')
            else:
                messages.error(request, 'No messages selected for deletion.')
            return redirect('users:client_message_view')  # Adjust URL name as needed

        # Handle sending messages
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=client.user, receiver=selected_lawyer.user, content=content)
            messages.success(request, 'Message sent successfully!')
            return redirect('users:client_message_view')

    return render(request, 'users/client_message_template.html', {
        'selected_lawyer': selected_lawyer,
        'messages': messages_list,
    })


def client_message_success(request):
    return render(request,'users/message_success.html')