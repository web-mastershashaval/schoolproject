# Generated by Django 5.1 on 2024-10-22 08:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0005_lawyer_phone'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lawyer_appointments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='lawyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lawyer_appointments', to='lawyers.lawyer'),
        ),
    ]