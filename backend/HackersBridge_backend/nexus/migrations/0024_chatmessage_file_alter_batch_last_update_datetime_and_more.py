# Generated by Django 5.1.5 on 2025-06-24 07:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexus', '0023_ticket_assigned_to_ticket_priority_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='chat_files/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'pdf'])]),
        ),
        migrations.AlterField(
            model_name='batch',
            name='last_update_datetime',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='batchstudentassignment',
            name='student_batch_status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='message',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='studentbatchrequest',
            name='request_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Removed', 'Removed')], default='Pending', max_length=50),
        ),
    ]
