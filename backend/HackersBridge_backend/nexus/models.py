from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.timezone import now
import datetime
import random
import string
from django.core.validators import FileExtensionValidator




class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    user_agent = models.TextField()
    blocked_at = models.DateTimeField(auto_now_add=True)
    unblock_at = models.DateTimeField()

    def is_active(self):
        return self.unblock_at > timezone.now()

    def __str__(self):
        return f"{self.ip_address} blocked until {self.unblock_at}"





class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('coordinator', 'Coordinator'),
        ('counsellor', 'Counsellor'),
        ('trainer', 'Trainer'),
        ('student', 'Student'),
    ]

    email = models.EmailField(unique=True)  # Ensure email is unique
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    first_login = models.BooleanField(default=True)  # Track first login

    REQUIRED_FIELDS = ['email']  # Keep 'username' as the primary identifier

    def __str__(self):
        return self.username



class OTPVerification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return now() > self.created_at + datetime.timedelta(minutes=5)  # Expire in 5 min

    @classmethod
    def delete_expired_otp(cls):
        cls.objects.filter(created_at__lt=now() - datetime.timedelta(minutes=5)).delete()



class Timeslot(models.Model):
    SPECIAL_SLOTS = [
        ('Normal', 'Normal'),
        ('Special', 'Special'),
    ]

    WEEK_TYPES = [
    ('Weekdays', 'Weekdays'),
    ('Weekends', 'Weekends'),
    ('Both', 'Both'),  # New option for covering both weekdays & weekends
    ]

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    gen_time = models.DateTimeField(default=timezone.now)
    week_type = models.CharField(max_length=10, choices=WEEK_TYPES, default='Weekdays')
    special_time_slot = models.CharField(max_length=20, choices=SPECIAL_SLOTS, null=True, blank=True, default='Normal')

    def __str__(self):
        special_slot = self.special_time_slot if self.special_time_slot else "Regular"
        return f"{self.start_time} - {self.end_time} ({special_slot}, {self.week_type})"



class Course(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    certification_body = models.CharField(max_length=25, null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True, unique=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name



class Location(models.Model):
    code = models.CharField(max_length=10, unique=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    locality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.locality



class Book(models.Model):
    STATUS = [
        ('Available', 'Available'),
        ('Not', 'Not'),
    ]

    book_id = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=25)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    stock = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default='Available')  # Fixed default value
    last_update_user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='book_update'
    )
    last_update_datetime = models.DateTimeField(default=timezone.now)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name



class Batch(models.Model):
    MODE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
        ('Hybrid', 'Hybrid'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Both', 'Both'),
    ]

    PREFERRED_WEEK_CHOICES = [
        ('Weekdays', 'Weekdays'),
        ('Weekends', 'Weekends'),
        ('Both', 'Both'),
    ]

    STATUS = [
        ('Hold', 'Hold'),
        ('Running', 'Running'),
        ('Upcoming', 'Upcoming'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]

    batch_id = models.CharField(max_length=60, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    trainer = models.ForeignKey("Trainer.Trainer", null=True, blank=True, on_delete=models.CASCADE)
    
    # ✅ Fix Student Model Reference
    student = models.ManyToManyField("Student.Student", through="BatchStudentAssignment", blank=True)

    status = models.CharField(max_length=10, null=True, blank=True, choices=STATUS, default='Upcoming')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, null=False, blank=False)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    preferred_week = models.CharField(max_length=10, choices=PREFERRED_WEEK_CHOICES, default='Weekdays')
    batch_time = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    batch_coordinator = models.ForeignKey("Coordinator.Coordinator", on_delete=models.SET_NULL, null=True, blank=True)

    last_update_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='batch_update')
    batch_created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='batch_create')
    batch_link = models.CharField(max_length=200, null=True, blank=True)
    batch_create_datetime = models.DateTimeField(default=timezone.now)
    last_update_datetime = models.DateTimeField(auto_now=True)
    gen_time = models.DateTimeField(default=timezone.now)

    @property
    def student_count(self):
        return self.student.count()

    def __str__(self):
        return f"Batch {self.batch_id} ({self.course.name})"



class BatchStudentAssignment(models.Model):

    student_batch_status = [
        ('Active','Active'),
        ('Inactive','Inactive'),
    ]
    # ✅ Fix Student ForeignKey Reference
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    student = models.ForeignKey("Student.Student", on_delete=models.CASCADE)
    coordinator = models.ForeignKey("Coordinator.Coordinator", on_delete=models.SET_NULL, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)
    student_batch_status = models.CharField(max_length=10, null=True, blank=True, choices=student_batch_status, default='Active')
    last_update_datetime = models.DateTimeField(default=timezone.now)
    add_in_batch_email_sent = models.BooleanField(default=False)
    add_in_batch_email_sent_at = models.DateTimeField(null=True, blank=True)
    batch_completed_email_sent = models.BooleanField(default=False)
    batch_completed_email_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('batch', 'student')

    def __str__(self):
        return f"{self.student.name} added by {self.coordinator.coordinator_id if self.coordinator else 'Unknown'}"



class Attendance(models.Model):
    STUDENT_ATTENDANCE_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    student = models.ForeignKey("Student.Student", on_delete=models.CASCADE)

    trainer = models.ForeignKey("Trainer.Trainer", on_delete=models.SET_NULL, null=True, blank=True)
    trainer_name = models.CharField(max_length=50, null=True, blank=True, editable=False)

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_name = models.CharField(max_length=100, null=True, blank=True, editable=False)

    time_slot = models.ForeignKey(Timeslot, on_delete=models.SET_NULL, null=True, blank=True)

    date = models.DateField()
    gen_time = models.DateTimeField(default=timezone.now)
    
    attendance = models.CharField(max_length=50, choices=STUDENT_ATTENDANCE_CHOICES)

    def save(self, *args, **kwargs):
        # Auto-fill trainer_name and course_name if related object is present
        if self.trainer:
            self.trainer_name = str(self.trainer)
        if self.course:
            self.course_name = str(self.course)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.date} - {self.attendance}"



class StudentBatchRequest(models.Model):
    REQUEST_BATCH_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Removed', 'Removed'),
    ]

    student = models.ForeignKey('Student.Student', on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=50, default='Batch Request')
    request_status = models.CharField(max_length=50, choices=REQUEST_BATCH_CHOICES, default='Pending')

    def __str__(self):      
        return f"{self.student} - {self.batch}"



{
# class Ticket(models.Model):
#     STATUS_CHOICES = [
#         ('Open', 'Open'),
#         ('In Progress', 'In Progress'),
#         ('Resolved', 'Resolved'),
#         ('Closed', 'Closed'),
#     ]

#     ISSUE_TYPE = [
#         ('Book','Book'),
#         ('Batch','Batch'),
#         ('Certificate','Certificate'),
#         ('Internet','Internet'),
#         ('Unable to receive OTP','Unable to receive OTP'),
#         ('Management (chairs , labs)','Management (chairs , labs)'),
#         ('Fee','Fee'),
#         ('Other','Other')
#     ]

#     student = models.ForeignKey('Student.Student', on_delete=models.CASCADE, related_name='tickets')
#     title = models.CharField(max_length=255)
#     ticket_id = models.CharField(max_length=5, unique=True, editable=False, blank=True)
#     issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE, default='Other')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.student.enrollment_no} - {self.issue_type} - {self.title} - {self.status}"

#     def save(self, *args, **kwargs):
#         if not self.ticket_id:
#             self.ticket_id = self.generate_unique_ticket_id()
#         super().save(*args, **kwargs)

#     def generate_unique_ticket_id(self):
#         while True:
#             random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
#             if not Ticket.objects.filter(ticket_id=random_id).exists():
#                 return random_id
            


# class TicketChat(models.Model):
#     SENDER_CHOICES = [
#         ('student', 'student'),
#         ('coordinator', 'coordinator'),
#         ('admin', 'admin'),
#     ]

#     STATUS_CHOICES = [
#         ('Open', 'Open'),
#         ('Not Open', 'Not Open'),
#     ]

#     ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='chats')
#     sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
#     message = models.TextField()
#     message_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Open')
#     gen_time = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.ticket.student.enrollment_no} - {self.sender} - {self.gen_time}"

}



class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Answered', 'Answered'),
        ('Your-Query', 'Your-Query'),
        ('Closed', 'Closed'),
    ]

    ISSUE_TYPE_CHOICES = [
        ('Book', 'Book'),
        ('Batch', 'Batch'),
        ('Certificate', 'Certificate'),
        ('Internet', 'Internet'),
        ('Unable to receive OTP', 'Unable to receive OTP'),
        ('Management (chairs , labs)', 'Management (chairs , labs)'),
        ('Fee', 'Fee'),
        ('Other', 'Other')
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]

    student = models.ForeignKey('Student.Student', on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=255)
    ticket_id = models.CharField(max_length=5, unique=True, editable=False, blank=True)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, default='Other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Raise')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Low')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.enrollment_no} - {self.issue_type} - {self.title} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_unique_ticket_id()
        super().save(*args, **kwargs)

    def generate_unique_ticket_id(self):
        while True:
            random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            if not Ticket.objects.filter(ticket_id=random_id).exists():
                return random_id


class TicketChat(models.Model):
    SENDER_CHOICES = [
        ('student', 'student'),
        ('coordinator', 'coordinator'),
        ('admin', 'admin'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Not Open', 'Not Open'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='chats')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    message = models.TextField()
    message_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Open')
    gen_time = models.DateTimeField(default=timezone.now)
    open_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.ticket.student.enrollment_no} - {self.sender} - {self.gen_time}"



class Announcement(models.Model):
    ANNOUNCEMENT_TYPE_CHOICES = [
        ('Specific', 'Specific'),
        ('Overall', 'Overall')
    ]
    
    subject = models.CharField(max_length=50)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='announcement/', null=True, blank=True)
    batch = models.ManyToManyField(Batch, blank=True)
    trainer = models.ManyToManyField('Trainer.Trainer', blank=True)
    student = models.ManyToManyField('Student.Student', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    gen_time = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    announcement_type = models.CharField(max_length=10, choices=ANNOUNCEMENT_TYPE_CHOICES, default='Overall')

    def __str__(self):
        return f"{self.subject} - created by {self.created_by}"


class WelcomeEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"
    

class StartBatchEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"


class ComplateBatchEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"


class CancelBatchEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"


class AttendanceWarningEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"
    

class TerminationBatchEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"
    

class ExamAnnouncementEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"
    

class CustomEmail(models.Model):
    
    student = models.ManyToManyField('Student.Student', blank=True)
    email_opened = models.BooleanField(default=False)
    email_send_date = models.DateTimeField(auto_now=True)
    email_subject = models.CharField(max_length=150, blank=True, null=True)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    gen_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.email_subject} - Send by {self.send_by}"


{

# class Chats(models.Model):
#     batch = models.ForeignKey('Batch', on_delete=models.CASCADE)
#     message = models.TextField(null=True, blank=True)
#     gen_time = models.DateTimeField(default=timezone.now)

#     # Generic sender field (could be Student, Trainer, or Coordinator)
#     sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     sender_object_id = models.PositiveIntegerField()
#     sender = GenericForeignKey('sender_content_type', 'sender_object_id')

#     def __str__(self):
#         return f"{self.sender} - {self.message[:30]}"

}



class Chats(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat - Batch: {self.batch.name}"


class ChatMessage(models.Model):
    SENDER_CHOICES = [
        ('student', 'student'),
        ('trainer', 'trainer'),
        ('coordinator', 'coordinator'),
        ('admin', 'admin'),
    ]

    chat = models.ForeignKey(Chats, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=20, choices=SENDER_CHOICES)
    send_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    message = models.TextField(blank=True)
    file = models.FileField(
        upload_to='chat_files/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'pdf'])]
    )
    gen_time = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        sender_name = self.send_by.name if self.send_by else "Unknown"
        return f"{sender_name} - {self.sender} - {self.gen_time.strftime('%Y-%m-%d %H:%M:%S')}"