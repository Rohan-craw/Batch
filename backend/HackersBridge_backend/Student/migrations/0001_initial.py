# Generated by Django 5.1.5 on 2025-02-05 05:36

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Coordinator', '0001_initial'),
        ('Counsellor', '0001_initial'),
        ('nexus', '0002_coordinator_counsellor_course_location_timeslot_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollment_no', models.CharField(max_length=100, unique=True)),
                ('date_of_joining', models.DateField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('phone', models.CharField(max_length=15, unique=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('language', models.CharField(choices=[('English', 'English'), ('Hindi', 'Hindi'), ('Both', 'Both')], max_length=10)),
                ('guardian_name', models.CharField(blank=True, max_length=100, null=True)),
                ('guardian_no', models.CharField(blank=True, max_length=15, null=True)),
                ('mode', models.CharField(choices=[('Online', 'Online'), ('Offline', 'Offline')], max_length=10)),
                ('preferred_week', models.CharField(choices=[('Weekdays', 'Weekdays'), ('Weekends', 'Weekends'), ('Hybrid', 'Hybrid')], max_length=10)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Leave', 'Leave'), ('Inactive', 'Inactive')], default='Active', max_length=10, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='student/profile_pics/')),
                ('course_counsellor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Counsellor.counsellor')),
                ('location', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='nexus.location')),
                ('support_coordinator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Coordinator.coordinator')),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Not Started'), ('ongoing', 'Ongoing'), ('completed', 'Completed')], default='not_started', max_length=20)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='nexus.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Student.student')),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.AddField(
            model_name='student',
            name='courses',
            field=models.ManyToManyField(through='Student.StudentCourse', to='nexus.course'),
        ),
    ]
