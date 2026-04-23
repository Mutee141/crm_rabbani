from django.db import models
from django.utils import timezone
from datetime import datetime, date, time


# -------------------- CHOICES --------------------

DESIGNATION_CHOICES = [
    ("Advisor to CEO", "Advisor to CEO"),
    ("Assistant", "Assistant"),
    ("BDE", "BDE"),
    ("Cameraman", "Cameraman"),
    ("Cleaner", "Cleaner"),
    ("Cook Assistant", "Cook Assistant"),
    ("Digital Marketing", "Digital Marketing"),
    ("Finance Manager", "Finance Manager"),
    ("GM", "GM"),
    ("Graphic Designer", "Graphic Designer"),
    ("Manager", "Manager"),
    ("HR Assistant", "HR Assistant"),
    ("HR Officer", "HR Officer"),
    ("Manager Office Boy", "Manager Office Boy"),
    ("Operation Manager", "Operation Manager"),
    ("Project Manager", "Project Manager"),
    ("S&M Manager", "S&M Manager"),
    ("Sales Executive", "Sales Executive"),
    ("Team Leader", "Team Leader"),
]

DEPARTMENT_CHOICES = [
    ("Accounts", "Accounts"),
    ("Finance", "Finance"),
    ("HR", "HR"),
    ("Kitchen", "Kitchen"),
    ("Lower Management", "Lower Management"),
    ("Marketing", "Marketing"),
    ("Media & PR", "Media & PR"),
    ("Operations", "Operations"),
    ("Sales", "Sales"),
    ("Sales & Marketing", "Sales & Marketing"),
]

LEAVE_TYPES = [
    ("Short Leave", "Short Leave"),
    ("Full Leave", "Full Leave"),
    ("On Duty", "On Duty"),
]

STATUS_CHOICES = [
    ("Active", "Active"),
    ("Resigned", "Resigned"),
    ("Terminated", "Terminated"),
]


ATTENDANCE_STATUS = [
    ("Present", "Present"),
    ("Absent", "Absent"),
    ("Late", "Late"),
    ("Leave", "Leave"),
    ("Half Day", "Half Day"),
    ("On Duty", "On Duty"),
]

# -------------------- EMPLOYEE --------------------

class Employee(models.Model):
    name = models.CharField(max_length=120)
    father_name = models.CharField(max_length=120, blank=True, null=True)
    cnic_no = models.CharField(max_length=20, blank=True, null=True)

    emp_id = models.CharField(max_length=30, unique=True)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    date_of_joining = models.DateField(blank=True, null=True)
    old_emp_id = models.CharField(max_length=30, blank=True, null=True)

    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_no = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='employees/profile/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.emp_id})"



# -------------------- LEAVE --------------------

class Leave(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to="leave_attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} — {self.leave_type} on {self.date}"


# ---------------------------------------------------------
# -------------------- ATTENDANCE SYSTEM ------------------
# ---------------------------------------------------------

# 1️⃣ Attendance Upload Table
# No changes needed to Employee or AttendanceRecord, but ensure this one is correct:
class AttendanceUpload(models.Model):
    file = models.FileField(upload_to='attendance_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    record_count = models.IntegerField(default=0, null=True, blank=True) # Use this name
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Upload {self.id} - {self.status}"

class Record(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="records"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.employee} - {self.date}"



# 2️⃣ Attendance Schedule Table
class AttendanceSchedule(models.Model):
    SCHEDULE_TYPES = (
        ("Normal", "Normal"),
        ("Special", "Special"),
    )

    name = models.CharField(max_length=150)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



# 3️⃣ Attendance Records Table
class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ("Present", "Present"),
        ("Absent", "Absent"),
        ("Late", "Late"),
        ("Full Leave", "Full Leave"),
        ("Short Leave", "Short Leave"),
        ("On Duty", "On Duty"),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, editable=False)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES, editable=False)
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True) # Changed to allow null
    check_out = models.TimeField(null=True, blank=True) # Changed to allow null
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Present")
    remarks = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ("employee", "date")
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        # 1. Auto-fill info from Employee
        if self.employee:
            self.department = self.employee.department
            self.designation = self.employee.designation

        # 2. Calculate Hours safely
        if self.check_in and self.check_out:
            try:
                # Use a reference date to calculate time difference
                d1 = datetime.combine(date.today(), self.check_in)
                d2 = datetime.combine(date.today(), self.check_out)
                
                # Handle night shift (if check_out is technically next day)
                if d2 < d1:
                    self.total_hours = 0 # Or logic for overnight shifts
                else:
                    diff = d2 - d1
                    self.total_hours = round(diff.total_seconds() / 3600, 2)
            except Exception:
                self.total_hours = 0
        else:
            self.total_hours = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.emp_id} - {self.date}"