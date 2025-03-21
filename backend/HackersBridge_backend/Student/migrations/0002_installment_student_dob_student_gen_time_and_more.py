# Generated by Django 5.1.5 on 2025-02-06 09:54

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coordinator', '0001_initial'),
        ('Counsellor', '0001_initial'),
        ('Student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Installment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_fee', models.FloatField(blank=True, null=True)),
                ('down_payment', models.FloatField(blank=True, null=True)),
                ('pay_date', models.DateField(null=True)),
                ('emi_day', models.IntegerField(blank=True, null=True)),
                ('total_emi_amount', models.FloatField(blank=True, null=True)),
                ('emi_amount', models.FloatField(blank=True, null=True)),
                ('one_time', models.BooleanField(default=False)),
                ('transition_id', models.CharField(blank=True, max_length=100, null=True)),
                ('pay_mode', models.CharField(blank=True, choices=[('cash', 'cash'), ('online', 'online')], max_length=50, null=True)),
                ('paid_fees', models.FloatField(blank=True, null=True)),
                ('due_fees', models.FloatField(blank=True, null=True)),
                ('total_ins', models.IntegerField()),
                ('ins_paid', models.IntegerField()),
                ('ins_rem', models.IntegerField()),
                ('is_completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='gen_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='student',
            name='last_update_coordinated',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_update', to='Coordinator.coordinator'),
        ),
        migrations.AddField(
            model_name='student',
            name='last_update_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='student',
            name='note',
            field=models.TextField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='student_assing_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_assing', to='Coordinator.coordinator'),
        ),
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Leave', 'Leave'), ('Inactive', 'Inactive')], default='Active', max_length=25, null=True),
        ),
        migrations.CreateModel(
            name='FeesRecords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_date', models.DateField(null=True)),
                ('payment', models.FloatField(blank=True, null=True)),
                ('pay_mode', models.CharField(choices=[('cash', 'cash'), ('online', 'online')], max_length=10)),
                ('transition_id', models.CharField(blank=True, max_length=100, null=True)),
                ('counsellor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Counsellor.counsellor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Student.student')),
                ('installments', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Student.installment')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='installment',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='installment', to='Student.installment'),
        ),
    ]
