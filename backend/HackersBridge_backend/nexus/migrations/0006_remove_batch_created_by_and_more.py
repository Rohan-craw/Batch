# Generated by Django 5.1.5 on 2025-02-08 10:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexus', '0005_alter_course_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='batch',
            name='last_update_coordinator',
        ),
        migrations.RemoveField(
            model_name='book',
            name='create_coordinator',
        ),
        migrations.RemoveField(
            model_name='book',
            name='last_update_coordinator',
        ),
        migrations.AddField(
            model_name='batch',
            name='batch_created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='batch_create', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='batch',
            name='last_update_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='batch_update', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='book_create_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='book_create', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='book',
            name='last_update_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='book_update', to=settings.AUTH_USER_MODEL),
        ),
    ]
