# Generated by Django 5.1.5 on 2025-02-11 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nexus', '0006_remove_batch_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='language',
            field=models.CharField(choices=[('English', 'English'), ('Hindi', 'Hindi'), ('Both', 'Both')], max_length=10),
        ),
    ]
