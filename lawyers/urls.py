from django.urls import path
from . import views


app_name='lawyers'

urlpatterns = [
    # dashboard and home linkd
    path('lawyers/lawyer_dashboard/', views.lawyer_dashboard_view, name='lawyer_dashboard'),
    path('home/', views.home_dashboard_view, name='home'),
    #lawyers profile links
    path('lawyer-profile', views.lawyer_profile_management, name='lawyer-profile'),
    path('create-profile/', views.profile_creation_view, name='profile_creation_view'),  
    #lawyers clients links
    path('lawyers/clients/', views.lawyer_clients_view, name='lawyers_clients'),
    path('clients/search/', views.client_search_view, name='client_search'),
    path('clients/delete/<int:client_id>/', views.delete_client_view, name='delete_client'), 
       # Appointment management URLs
    path('appointment/<int:lawyer_id>/', views.create_appointment_view, name='create_appointment_view'),
    path('appointments/edit/<int:appointment_id>/', views.edit_appointment_view, name='edit_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment_view, name='delete_appointment'),
    path('appointments/', views.appointment_list_view, name='appointments'),  # Add this if you have a list view
    # cases links
    path('case/', views.case_management_view, name='case_management'),
    path('case/delete/<int:case_id>/', views.delete_case_view, name='delete_case'),
    # links to money/payments
    path('payment/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('payment/delete/<int:payment_id>/', views.delete_payment_view, name='delete_payment'),

    # links to files  
    path('upload/', views.upload_file_view, name='upload_files'),
    path('delete/<int:file_id>/', views.delete_lawyer_file, name='delete_lawyer_file'),  

    path('message/', views.message_view, name='message_view'),

]