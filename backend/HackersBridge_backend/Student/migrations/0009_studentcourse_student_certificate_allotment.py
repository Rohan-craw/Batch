# Generated by Django 5.1.5 on 2025-02-25 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0008_studentcourse_certificate_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcourse',
            name='student_certificate_allotment',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
