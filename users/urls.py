from django.urls import path
from . import views
from django.views.generic import RedirectView

app_name = 'users'

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-up/', views.signup, name='sign-up'),
    path('sign-in/', views.signin, name='sign-in'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('user-category/', views.user_category_view, name='usercategory'),
    path('home/', views.home_dashboard_view, name='home'),
    path('logout/', views.logout_view, name='logout'),

    path('appointment/', views.create_appointment, name='appointment'),
    path('appointment/confirmation/', views.appointment_confirmation, name='appointment_confirmation'),
    path('appointments/manage/', views.manage_appointments, name='manage_appointments'),
    path('appointments/edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    
    path('casemanagement/', views.case_management_view, name='casemanagement'),
    path('documents/', views.documents_view, name='documents_view'),
    path('documents/delete/<int:document_id>/', views.delete_document, name='delete_document'),

    path('profile-form/', views.profile_management_view, name='profile_management_view'),
    path('create-profile/', views.create_profile_view, name='profile_creation'),

    path('payment/', views.payment_view, name='payment'),
    path('payment/success/', views.payment_success_view, name='payment_success'),

    path('upload_files/',views.upload_file_view, name='upload_file_view'),
    path('upload/', views.upload_file_view, name='upload_files'),
    
    path('choose-lawyer/', views.choose_lawyer, name='choose_lawyer'),  # Updated path
    path('select-lawyer/<int:lawyer_id>/', views.select_lawyer, name='select_lawyer'),  # If you have a separate view for selecting
    path('lawyers/<int:lawyer_id>/profile/', views.lawyer_profile_view, name='lawyer_profile'),
    
    path('lawyers/', RedirectView.as_view(url='/users/lawyers/', permanent=False)),

    path('messages/', views.client_message_view, name='client_message_view'),
    path('messages/success', views.client_message_success, name='client_message_success'),
]
