from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    dept_name = models.CharField(max_length=200, default="Department of Information Science and Engineering")
    code = models.CharField(max_length=50, default="ISE")
    location = models.CharField(max_length=255, default="Main Academic Block, 2nd Floor, MCE Hassan")
    contact_number = models.CharField(max_length=50, default="+91 8172 245085")

    def __str__(self):
        return self.dept_name


class Category(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Subject(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    semester = models.IntegerField(default=1)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True, default="")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['semester', 'code']


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('ROLE_ADMIN', 'Admin'),
        ('ROLE_FACULTY', 'Faculty'),
        ('ROLE_STUDENT', 'Student'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='ROLE_STUDENT')
    full_name = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True, default="")
    identifier = models.CharField(max_length=100, blank=True, default="")  # USN or Faculty ID
    current_semester = models.IntegerField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    enrolled_subjects = models.ManyToManyField(Subject, blank=True, related_name='enrolled_students')
    is_active_user = models.BooleanField(default=True)

    def __str__(self):
        role_label = "admin" if self.role == 'ROLE_ADMIN' else ("faculty" if self.role == 'ROLE_FACULTY' else "student")
        return f"{self.user.username}: {role_label}"

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"


class Resource(models.Model):
    CATEGORY_CHOICES = (
        ('LECTURE_NOTES', 'Lecture Notes'),
        ('LAB_MANUAL', 'Lab Manuals'),
        ('PREVIOUS_QUESTION_PAPER', 'Question Papers (PYQ)'),
        ('REFERENCE_BOOK', 'Reference Books'),
        ('PROJECT_REPO', 'Project Repos'),
        ('SOFTWARE_TOOL_GUIDE', 'Tool & Setup Guides'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='LECTURE_NOTES')
    semester = models.IntegerField(default=1)
    tags = models.CharField(max_length=500, blank=True, default="")
    
    file = models.FileField(upload_to='resources/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True, default="")
    original_file_name = models.CharField(max_length=255, blank=True, default="")
    file_download_uri = models.CharField(max_length=500, blank=True, default="")
    file_type = models.CharField(max_length=50, default='pdf')
    file_size = models.BigIntegerField(default=0)

    download_count = models.BigIntegerField(default=0)
    view_count = models.BigIntegerField(default=0)

    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_resources')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='resources')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.is_approved:
            self.status = 'Approved'
        elif self.status == 'Approved':
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class ResourceRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('FULFILLED', 'Fulfilled'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_requests')
    resource_name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, default="")
    semester = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource_name} ({self.user.username})"

    class Meta:
        verbose_name = "Resource request"
        verbose_name_plural = "Resource requests"
        ordering = ['-requested_at']


class ResourceComment(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_comments')
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.resource.title[:20]}"

    class Meta:
        ordering = ['-created_at']


class LabWorkstation(models.Model):
    STATUS_CHOICES = (
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
    )

    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=100, unique=True)
    specs = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='AVAILABLE')
    ip_address = models.CharField(max_length=100, default='172.16.10.101')

    def __str__(self):
        return f"{self.name} ({self.identifier})"


class WorkstationBooking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    )

    workstation = models.ForeignKey(LabWorkstation, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workstation_bookings')
    purpose = models.CharField(max_length=500)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    admin_remarks = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.workstation.identifier} booked by {self.user.username} [{self.status}]"

    class Meta:
        ordering = ['-created_at']
