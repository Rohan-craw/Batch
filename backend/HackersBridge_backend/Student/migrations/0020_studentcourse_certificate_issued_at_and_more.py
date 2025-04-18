# Generated by Django 5.1.5 on 2025-04-12 05:39

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0019_remove_studentcourse_gen_time'),
        ('nexus', '0020_rename_book_stock_book_stock_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcourse',
            name='certificate_issued_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentcourse',
            name='student_book_allotment',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.CreateModel(
            name='BookAllotment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allotment_datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('allot_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('book', models.ManyToManyField(to='nexus.book')),
                ('student', models.ManyToManyField(to='Student.student')),
            ],
        ),
    ]
