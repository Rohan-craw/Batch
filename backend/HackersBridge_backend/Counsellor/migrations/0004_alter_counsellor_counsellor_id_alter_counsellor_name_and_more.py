# Generated by Django 5.1.5 on 2025-02-25 05:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Counsellor', '0003_alter_counsellor_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='counsellor',
            name='counsellor_id',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='counsellor',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='counsellor',
            name='phone',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
