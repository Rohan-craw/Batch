# Generated by Django 5.1.5 on 2025-02-13 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Counsellor', '0002_counsellor_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counsellor',
            name='status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=10, null=True),
        ),
    ]
