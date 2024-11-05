from django.contrib import admin
from .models import Lawyer,Appointment,CaseManagement,Payment,UploadFiles
# Register your models here.

@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number','phone', 'specialties','bio')

admin.site.register(Appointment) 
admin.site.register(CaseManagement)   
admin.site.register(Payment)
admin.site.register(UploadFiles)
