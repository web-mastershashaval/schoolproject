from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import  Appointment, UploadFiles, Payment,Lawyer,Message

from lawyers.models import CaseManagement as LawyerCaseManagement
from users.models import CaseManagement as UserCaseManagement
from lawyers.models import UploadFiles as LawyerUploadFiles
from users.models import UploadFiles as ClientUploadFiles
from lawyers.models import Payment as LawyerPayment
from users.models import Payment as ClientPayment 
from users.models import Appointment as UserAppointment  # Import user appointments
from lawyers.models import Appointment as LawyerAppointment  # Import lawyer appointments

from .forms import AppointmentForm,  CaseForm, UploadFileForm ,LawyerProfileForm,PaymentForm,MessageForm
from django.contrib.auth.models import Group
import calendar
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from .decorator import lawyer_required
from .forms import LawyerProfileForm
from users.models import Client
import users
import logging
from users.models import Client
from django.db.models import Q


logger = logging.getLogger(__name__)
# Create your views here.

@login_required
@lawyer_required
def lawyer_dashboard_view(request):
    lawyer = get_object_or_404(Lawyer, user=request.user)
    return render(request, 'lawyers/lawyer_dashboard.html', {'lawyer': lawyer})
@login_required
@lawyer_required
def home_dashboard_view(request):
    now = timezone.now()
    
    # Get the logged-in lawyer
    lawyer = get_object_or_404(Lawyer, user=request.user)
    
    # Fetch clients for this lawyer
    clients = Client.objects.filter(selected_lawyer=lawyer)

    # Fetch all appointments for these clients
    appointments =users.models.Appointment.objects.filter(user__in=clients.values_list('user', flat=True)).order_by('-appointment_date')
    
    # Fetch cases associated with clients' users
    cases = users.models.CaseManagement.objects.filter(user__in=clients.values_list('user', flat=True)).order_by('-date')

    #fetching the payments from clients
    payment = users.models.Payment.objects.filter(user__in=clients.values_list('user', flat=True)).order_by('-created_at')
    
    # Get only the last two appointments
    last_two_appointments = appointments[:2]
    last_two_cases = cases[:2]
    last_two_payments = payment[:2]
    
    # Get only the last two clients (or however many you want)
    last_two_clients = clients[:2]

    # Get the last two payments for each client
    last_two_payments = {}
    for client in last_two_clients:
        payments = Payment.objects.filter(user=client.user).order_by('-created_at')[:2]
        last_two_payments[client] = payments

    has_upcoming_appointments = appointments.filter(appointment_date__gt=now).exists()
     # Get or create the user's profile
    

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

    return render(request, 'lawyers/lawyer_home.html', {
        'lawyer_id': lawyer.id,
        'lawyer': lawyer,
        'has_upcoming_appointments': has_upcoming_appointments,
        'has_unread_messages': has_unread_messages,
        'calendar': calendar_days,
        'appointments': last_two_appointments,
        'cases': last_two_cases,
        'clients': last_two_clients,
       
        'last_two_payments': last_two_payments,  # Pass the payments to the template
    }) 


@login_required
@lawyer_required
def lawyer_dashboard_view(request):
    lawyer = get_object_or_404(Lawyer, user=request.user)

    # Get clients that selected this lawyer
    clients = Client.objects.filter(selected_lawyer=lawyer)

    # Get related appointments, cases, payments, and uploaded files
    appointments = Appointment.objects.filter(client__in=clients.values_list('user', flat=True))
    cases = LawyerCaseManagement.objects.filter(lawyer=lawyer)
    payments = Payment.objects.filter(user__in=clients.values_list('user', flat=True))
    uploaded_files = UploadFiles.objects.filter(user__in=clients.values_list('user', flat=True))

    # Initialize forms
    appointment_form = AppointmentForm()
    profile_form = LawyerProfileForm()
    case_management_form = CaseForm()
    upload_file_form = UploadFileForm()
    payment_form = PaymentForm()
    message_form = MessageForm()  # Correct initialization

    if request.method == 'POST':
        if 'appointment' in request.POST:
            appointment_form = handle_appointment_form(request)
        elif 'case' in request.POST:
            case_management_form = handle_case_management_form(request)
        elif 'upload_files' in request.POST:
            upload_file_form = handle_upload_file_form(request)
        elif 'payment' in request.POST:
            payment_form = handle_payment_form(request)
        elif 'messages' in request.POST:
            message_form = handle_message_form(request)

        return redirect('lawyers:lawyer_dashboard')  # Redirect to avoid resubmission

    return render(request, 'lawyers/lawyer_dashboard.html', {
        'user': request.user,
        'appointments': appointments,
        'cases': cases,
        'clients': clients,
        'payments': payments,
        'uploaded_files': uploaded_files,
        'appointment_form': appointment_form,
        'profile_form': profile_form,
        'case_management_form': case_management_form,
        'upload_file_form': upload_file_form,
        'payment_form': payment_form,
        'message_form': message_form,
        'lawyer': lawyer,  # Ensure you pass the lawyer object here
    })


def handle_appointment_form(request, lawyer_id):
    form = AppointmentForm(request.POST)
    if form.is_valid():
        appointment = form.save(commit=False)
        appointment.lawyer = request.user.lawyer  # Associate the logged-in lawyer
        appointment.save()
        messages.success(request, 'Appointment created successfully!')
        return redirect('lawyers:appointments')  # Redirect to appointments list
    else:
        messages.error(request, 'There was an error with your appointment form.')
    return form

def handle_message_form(request, lawyer_id):
    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.lawyer = request.user.lawyer  # Associate the logged-in lawyer
        message.save()
        messages.success(request, 'Message sent successfully!')
        return redirect('lawyers:message_view', lawyer_id=lawyer_id)  # Pass the lawyer_id here
    else:
        messages.error(request, 'There was an error with your message form.')
    return form


@login_required
@lawyer_required  
def create_appointment_view(request, lawyer_id):
    logger.info(f"User {request.user} is trying to access appointment management.")

    if request.method == 'POST':
        appointment_form = handle_appointment_form(request, lawyer_id)  # Handle form submission
    else:
        appointment_form = AppointmentForm()  # Initialize your form

    lawyer = get_object_or_404(Lawyer, id=lawyer_id)  # Get the lawyer safely
    lawyer_appointments = Appointment.objects.filter(lawyer=lawyer)
    
    # Fetch clients and their appointments
    clients = Client.objects.filter(selected_lawyer=lawyer)
    client_appointments = UserAppointment.objects.filter(user__in=clients.values('user'))

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        lawyer_appointments = lawyer_appointments.filter(
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(state_problem__icontains=search_query)
        )
        client_appointments = client_appointments.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(state_problem__icontains=search_query)
        )

    return render(request, 'lawyers/appointment_form.html', {
        'appointment_form': appointment_form,
        'lawyer_appointments': lawyer_appointments,
        'client_appointments': client_appointments,
        'lawyer_id': lawyer.id,
    })

@login_required
@lawyer_required
def edit_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, lawyer=request.user.lawyer)

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated successfully!')
            return redirect('lawyers:appointments')  # Redirect to appointments list
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'lawyers/edit_appointment.html', {
        'form': form,
        'appointment': appointment,
    })

@login_required
@lawyer_required
def appointment_list_view(request):
    lawyer = request.user.lawyer
    appointments = Appointment.objects.filter(lawyer=lawyer)
    
    return render(request, 'lawyers/appointment_list.html', {
        'appointments': appointments,
    })


@login_required
@lawyer_required
def delete_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, lawyer=request.user.lawyer)
    appointment.delete()
    messages.success(request, 'Appointment deleted successfully!')
    return redirect('lawyers:appointments')  # Ensure this redirects to the appointments list

@login_required
def lawyer_profile_management(request):
    try:
        lawyer = Lawyer.objects.get(user=request.user)
    except Lawyer.DoesNotExist:
        messages.error(request, 'No lawyer profile found. Please create one.')
        return redirect('lawyers:profile_creation_view')

    if request.method == 'POST':
        form = LawyerProfileForm(request.POST, request.FILES, instance=lawyer)  # Include request.FILES
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('lawyers:lawyer-profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LawyerProfileForm(instance=lawyer)

    return render(request, 'lawyers/lawyer_profile.html', {
        'form': form,
        'lawyer': lawyer,
        'lawyer_id': lawyer.id
    })


@login_required
@lawyer_required
def profile_creation_view(request):
    if request.method == 'POST':
        form = LawyerProfileForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            lawyer = form.save(commit=False)
            lawyer.user = request.user
            lawyer.save()
            messages.success(request, 'Profile created successfully.')
            return redirect('lawyers:lawyer_dashboard')
    else:
        form = LawyerProfileForm()
    
    return render(request, 'lawyers/profile_creation.html', {'form': form})


def handle_case_management_form(request):
    form = CaseForm(request.POST)
    if form.is_valid():
        case = form.save(commit=False)
        case.lawyer = request.user.lawyer  # Associate the logged-in lawyer
        case.save()
        messages.success(request, 'Case saved successfully!')
    else:
        messages.error(request, 'There was an error with your case management form.')
    return form


@login_required
@lawyer_required
def case_management_view(request):
    logger.info(f"User {request.user} is trying to access case management.")

    # Fetch the lawyer instance
    lawyer = request.user.lawyer

    if request.method == 'POST':
        case_management_form = handle_case_management_form(request)
    else:
        case_management_form = CaseForm()

    # Fetch cases filed by the lawyer using the LawyerCaseManagement model
    lawyer_cases = LawyerCaseManagement.objects.filter(lawyer=lawyer)

    # Ensure the user is a lawyer and fetch clients
    clients = Client.objects.filter(selected_lawyer=lawyer) if hasattr(lawyer, 'user') else Client.objects.none()

    # Fetch all cases associated with these clients' users from the UserCaseManagement model
    client_cases = UserCaseManagement.objects.filter(user__in=clients.values('user'))

    # Combine both QuerySets if needed
    all_cases = list(lawyer_cases) + list(client_cases)

    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        lawyer_cases = lawyer_cases.filter(
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(case_title__icontains=search_query) |
            Q(case_description__icontains=search_query)
        )

        client_cases = client_cases.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(case_title__icontains=search_query) |
            Q(case_description__icontains=search_query)
        )

    return render(request, 'lawyers/case_managment_form.html', {
        'case_management_form': case_management_form,
        'lawyer_cases': lawyer_cases,
        'client_cases': client_cases,
        'all_cases': all_cases,
        'lawyer_id': lawyer.id,  # Pass the lawyer ID to the template
    })



@login_required
@lawyer_required
def delete_case_view(request, case_id):
    case = get_object_or_404(LawyerCaseManagement, id=case_id, lawyer=request.user.lawyer)
    case.delete()
    messages.success(request, 'Case deleted successfully!')
    return redirect('lawyers:case_management')


def handle_upload_file_form(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_file = form.save(commit=False)
        uploaded_file.user = request.user  # Associate the user
        uploaded_file.save()
        messages.success(request, 'File uploaded successfully!')
    else:
        messages.error(request, 'There was an error uploading your file.')
    return form

@login_required
@lawyer_required
def upload_file_view(request):
    search_query = request.GET.get('search', '')
    lawyer_id = request.user.lawyer.id  # Get the lawyer ID

    # Fetch lawyer's uploaded files
    lawyer_files = LawyerUploadFiles.objects.filter(user=request.user)

    # Fetch client's uploaded files associated with the lawyer
    client_files = ClientUploadFiles.objects.filter(user__lawyer=request.user.lawyer)

    # Implement search functionality for lawyer's files
    if search_query:
        lawyer_files = lawyer_files.filter(file__icontains=search_query)
        client_files = client_files.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(file__icontains=search_query)
        )

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = form.save(commit=False)
            upload_file.user = request.user  # Associate uploaded file with the user
            upload_file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('lawyers:upload_files')
    else:
        form = UploadFileForm()

    return render(request, 'lawyers/upload_file_form.html', {
        'form': form,
        'lawyer_files': lawyer_files,
        'client_files': client_files,
        'search_query': search_query,
        'lawyer_id': lawyer_id,  # Pass the lawyer ID to the template
    })


@login_required
@lawyer_required
def delete_lawyer_file(request, file_id):
    file = get_object_or_404(UploadFiles, id=file_id, user=request.user)
    file.delete()
    messages.success(request, 'File deleted successfully!')
    return redirect('lawyers:upload_files')



@login_required
@lawyer_required
def client_list_view(request):
    clients_group = Group.objects.get(name='Clients')
    clients = clients_group.user_set.all()

    lawyer_id = request.user.lawyer.id  # Get the lawyer ID

    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        clients = clients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(state_problem__icontains=search_query)
        )
    
    return render(request, 'lawyers/lawyers_clients.html', {
        'clients': clients,
        'lawyer_id': lawyer_id,  # Pass the lawyer ID to the template
    })


@login_required
def delete_client_view(request, client_id):
    client = get_object_or_404(User, id=client_id)
    client.delete()  # Optionally handle related data if needed
    messages.success(request, 'Client deleted successfully.')
    return redirect('lawyers:clients')


@login_required
@lawyer_required
def payment_view(request):
    lawyer = get_object_or_404(Lawyer, user=request.user)
    lawyer_id = lawyer.id  # Get the lawyer ID

    if request.method == 'POST':
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment = payment_form.save(commit=False)
            client = payment_form.cleaned_data['user']

            # Ensure the client has an associated User instance
            if hasattr(client, 'user'):
                payment.user = client.user  # Correctly assign the User instance
                payment.save()
                messages.success(request, 'Payment recorded successfully!')
                return redirect('lawyers:payment_view')
            else:
                messages.error(request, 'Selected client does not have an associated user.')
    else:
        payment_form = PaymentForm()

    # Fetch payments associated with the lawyer and their clients
    lawyer_payments = LawyerPayment.objects.filter(user=request.user)
    client_payments = ClientPayment.objects.filter(user__in=lawyer.clients.values('user'))

    # Implementing search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        lawyer_payments = lawyer_payments.filter(
            Q(amount__icontains=search_query) | 
            Q(status__icontains=search_query)
        )
        client_payments = client_payments.filter(
            Q(amount__icontains=search_query) | 
            Q(status__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    return render(request, 'lawyers/payment.html', {
        'lawyer': lawyer, 
        'payment_form': payment_form,
        'lawyer_payments': lawyer_payments,
        'client_payments': client_payments,
        'search_query': search_query,
        'lawyer_id': lawyer_id,  # Pass the lawyer ID to the template
    })


@login_required
@lawyer_required
def delete_payment_view(request, lawyer_id, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    payment.delete()
    messages.success(request, 'Payment deleted successfully!')
    return redirect('lawyers:payment_view')



@login_required
@lawyer_required
def payment_success_view(request):
    return render(request, 'lawyers/payment_success.html')

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
@lawyer_required
def lawyer_clients_view(request):
    lawyer = get_object_or_404(Lawyer, user=request.user)  # Fetch the logged-in lawyer
    clients = lawyer.clients.all()  # Get clients associated with the lawyer

    # Handle search query if needed
    search_query = request.GET.get('search', '')
    if search_query:
        clients = clients.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    return render(request, 'lawyers/lawyers_clients.html', {'lawyer': lawyer, 'clients': clients,'lawyer_id': lawyer.id})

from django.http import JsonResponse
@login_required
@lawyer_required
def client_search_view(request):
    search_query = request.GET.get('query', '')
    clients = []

    if search_query:
        clients = Client.objects.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        ).values('user__first_name', 'user__last_name', 'user__email')

    return JsonResponse(list(clients), safe=False)

@login_required
@lawyer_required
def message_view(request):
    lawyer = request.user.lawyer
    clients = lawyer.clients.all()
    selected_client = None
    messages_list = []

    if request.method == 'POST':
        # Check if the delete action is requested
        if 'delete_message' in request.POST:
            message_id = request.POST.get('message_id')
            try:
                message = Message.objects.get(id=message_id, sender=request.user)
                message.delete()
                messages.success(request, 'Message deleted successfully!')
            except Message.DoesNotExist:
                messages.error(request, 'Message not found.')

            return redirect('lawyers:message_view')  # Redirect to the same page

        # Handle sending a message
        client_id = request.POST.get('client_id')
        content = request.POST.get('content')
        selected_client = get_object_or_404(Client, id=client_id, selected_lawyer=lawyer)

        if request.user == selected_client.user:
            messages.error(request, "You cannot send messages to yourself.")
            return redirect('lawyers:message_view')

        if content:
            Message.objects.create(sender=request.user, receiver=selected_client.user, content=content)
            messages.success(request, 'Message sent successfully!')
            return redirect('lawyers:message_view')

    client_id = request.GET.get('client_id')
    if client_id:
        selected_client = get_object_or_404(Client, id=client_id, selected_lawyer=lawyer)
        messages_list = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=selected_client.user)) | 
            (Q(sender=selected_client.user) & Q(receiver=request.user))
        ).order_by('-timestamp')
    else:
        messages_list = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user)
        ).order_by('-timestamp')

    return render(request, 'lawyers/message_template.html', {
        'clients': clients,
        'selected_client': selected_client,
        'messages': messages_list,
    })
