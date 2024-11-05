from django.contrib import admin
from .models import Appointment,Profile,UploadFiles,CaseManagement,Payment
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate


# Register your models here.
admin.site.register(Appointment)
admin.site.register(Profile)
admin.site.register(CaseManagement)
admin.site.register(UploadFiles)
admin.site.register(Payment)


# Create a new group for clients
def create_client_group(sender, **kwargs):
    Group.objects.get_or_create(name='Clients')
# Connect the post_migrate signal to the create_client_group function
post_migrate.connect(create_client_group)

# create a lawyer group
# def create_lawyer_group(sender, **kwargs):
#     Group.objects.get_or_create(name='Lawyers')
# post_migrate.connect(create_lawyer_group)
