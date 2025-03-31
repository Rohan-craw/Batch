# Generated by Django 5.1.5 on 2025-03-31 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0014_alter_studentcourse_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentcourse',
            name='status',
            field=models.CharField(choices=[('Not Started', 'Not Started'), ('Ongoing', 'Ongoing'), ('Upcoming', 'Upcoming'), ('Completed', 'Completed'), ('Denied', 'Denied')], default='Not Started', max_length=20),
        ),
    ]
