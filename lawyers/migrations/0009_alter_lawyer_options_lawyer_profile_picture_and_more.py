# Generated by Django 5.1 on 2024-11-02 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lawyers', '0008_message_is_read'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lawyer',
            options={'verbose_name': 'Lawyer', 'verbose_name_plural': 'Lawyers'},
        ),
        migrations.AddField(
            model_name='lawyer',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='bio',
            field=models.TextField(default='sheria ni msumeno ukatao kuwili', help_text='A brief bio of the lawyer.', max_length=255),
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='cases',
            field=models.TextField(blank=True, help_text='Describe cases you have handled or are currently handling.', null=True),
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='phone',
            field=models.CharField(default='+254 ', help_text='Enter phone number in the format: +254XXXXXXXXX', max_length=15),
        ),
        migrations.AlterField(
            model_name='lawyer',
            name='specialties',
            field=models.CharField(help_text='List your specialties, e.g., Family Law, Criminal Defense.', max_length=100),
        ),
    ]
