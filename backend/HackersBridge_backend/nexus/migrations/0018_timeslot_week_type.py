# Generated by Django 5.1.5 on 2025-03-26 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexus', '0017_timeslot_special_time_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='week_type',
            field=models.CharField(choices=[('Weekdays', 'Weekdays'), ('Weekends', 'Weekends'), ('Both', 'Both')], default='Weekdays', max_length=10),
        ),
    ]
