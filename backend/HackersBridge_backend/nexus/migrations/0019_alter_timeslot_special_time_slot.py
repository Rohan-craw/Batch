# Generated by Django 5.1.5 on 2025-03-26 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexus', '0018_timeslot_week_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeslot',
            name='special_time_slot',
            field=models.CharField(blank=True, choices=[('Normal', 'Normal'), ('Special', 'Special')], default='Normal', max_length=20, null=True),
        ),
    ]
