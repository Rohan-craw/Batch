from django.db import models
from django.utils import timezone
from datetime import date
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
# from django.contrib.auth import

class Trainer(models.Model): 
    PREFERRED_LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Both','Both'),
    ]

    WEEKOFF = [
        ('Monday','Monday'),
        ('Tuesday','Tuesday'),
        ('Wednesday','Wednesday'),
        ('Thursday','Thursday'),
        ('Friday','Friday'),
        ('Saturday','Saturday'),
        ('Sunday','Sunday'),
    ]

    STATUS = [
        ('Active','Active'),
        ('Inactive','Inactive')
    ]

    trainer_id = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    date_of_joining = models.DateField(null=True, blank=True)
    experience = models.CharField(max_length=100, null=True, blank=True)
    course = models.ManyToManyField("nexus.Course", blank=True)
    timeslot = models.ManyToManyField("nexus.Timeslot", blank=True)
    languages = models.CharField(max_length=10, null=True, blank=True, choices=PREFERRED_LANGUAGE_CHOICES)
    weekoff = models.CharField(max_length=10, null=True, blank=True, choices=WEEKOFF)
    real_status = models.BooleanField(default=False)
    location = models.ForeignKey("nexus.Location", null=True, blank=True, on_delete=models.SET_NULL)
    is_teamleader =  models.BooleanField(default=False)
    teamleader = models.ForeignKey(
        'self', 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members',  # Allows access to all trainers under a leader
        limit_choices_to={'is_teamleader': True},
    )

    coordinator = models.ForeignKey("Coordinator.Coordinator", null=True, blank=True , on_delete=models.SET_NULL)
    leave_status = models.CharField(max_length=100, null=True, blank=True)
    leave_end_date = models.DateField(null=True, blank=True)
    leave_start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, null=True, blank=True, choices=STATUS, default='Active')
    status_change_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='trainer/profile_pics/', null=True, blank=True)  # Stores image path
    last_update_user = models.ForeignKey("nexus.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name='trainer_update')
    # last_update_user = models.ForeignKey("nexus.CustomUser", on_delete=models.CASCADE, related_name='trainer_update', null=True, blank=True)
    last_update_time = models.DateField(default=timezone.now)
    gen_time = models.DateTimeField(default=timezone.now)


    # Add audit log tracking
    history = AuditlogHistoryField()

    def calculate_inactive_days(self):
        """Calculate total days when the trainer was inactive."""
        inactive_periods = Trainer.objects.filter(
            id=self.id,
            status="Inactive",
            status_change_date__isnull=False
        ).order_by("status_change_date")

        inactive_days = 0
        previous_date = self.status_change_date  # Start from joining date
        

        for period in inactive_periods:
            if previous_date:
                inactive_days += (date.today() - previous_date).days
            previous_date = period.status_change_date

        return inactive_days
    

    def save(self, *args, **kwargs):
        if not self.trainer_id:
            self.trainer_id = self.generate_trainer_id()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
# Register Trainer model for audit logging
# auditlog.register(Trainer)
    
class TrainerBatchEndEmail(models.Model):
    trainers = models.ManyToManyField(Trainer, blank=True)
    batch = models.ManyToManyField("nexus.Batch", blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now_add=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject or 'No Subject'} - Sent by {self.send_by or 'System'}"