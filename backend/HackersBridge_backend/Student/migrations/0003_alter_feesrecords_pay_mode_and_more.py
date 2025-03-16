# Generated by Django 5.1.5 on 2025-02-07 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0002_installment_student_dob_student_gen_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feesrecords',
            name='pay_mode',
            field=models.CharField(blank=True, choices=[('cash', 'cash'), ('online', 'online')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='feesrecords',
            name='payment_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='ins_paid',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='ins_rem',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='installment',
            name='total_ins',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
