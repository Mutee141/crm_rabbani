from django.db import models
from django.contrib.auth.models import User




    # -----------------------------
    # USER PROFILE (Hierarchy)
    # -----------------------------
class Profile(models.Model):
        # Change 'profile' to 'gm_profile'
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='gm_profile')
        
        reporting_to = models.ForeignKey(
            User, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True, 
            related_name='managed_staff'
        )
        designation = models.CharField(max_length=50, default="Manager") 
        emp_id = models.CharField(max_length=20, unique=True, blank=True, null=True)

        def __str__(self):
            return f"{self.user.username} - {self.designation}"
        
        
from django.db import models

class Project(models.Model):
        PROJECT_TYPE_CHOICES = [
            ('SHOPPING_MALL', 'Shopping Mall'),
            ('HOUSING', 'Housing Scheme'),
            ('COMMERCIAL', 'Commercial Project'),
        ]
        STATUS_CHOICES = [
            ('UPCOMING', 'Upcoming'),
            ('LAUNCHED', 'Launched'),
            ('COMPLETED', 'Completed'),
        ]
        name = models.CharField(max_length=255)
        project_type = models.CharField(max_length=30, choices=PROJECT_TYPE_CHOICES)
        location = models.CharField(max_length=255)
        description = models.TextField(blank=True)
        launch_date = models.DateField()
        status = models.CharField(max_length=20, choices=STATUS_CHOICES)

        def __str__(self):
            return self.name

class ProjectUnit(models.Model):
        UNIT_TYPE_CHOICES = [
            ('SHOP', 'Shop'),
            ('1BED', '1 Bed Apartment'),
            ('2BED', '2 Bed Apartment'),
            ('3BED', '3 Bed Apartment'),
            ('4BED', '4 Bed Apartment'),
            ('OFFICE', 'Office'),
        ]
        FLOOR_CHOICES = [
            ('BASEMENT', 'Basement'),
            ('GROUND', 'Ground Floor'),
            ('1', '1st Floor'),
            ('2', '2nd Floor'),
            ('3', '3rd Floor'),
            ('OTHER', 'Other'),
        ]
        STATUS_CHOICES = [
            ('AVAILABLE', 'Available'),
            ('SOLD', 'Sold'),
        ]

        project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='units')
        unit_name = models.CharField(max_length=100)
        unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)
        total_units = models.PositiveIntegerField()
        floor = models.CharField(max_length=20, choices=FLOOR_CHOICES)
        area_size = models.FloatField(help_text="Area in sq ft")
        rate_per_sqft = models.FloatField()
        commission_percent = models.FloatField()
        price = models.FloatField(editable=False, null=True, blank=True) # Added null=True to help with initial validation
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

        def save(self, *args, **kwargs):
            # Calculate price before saving to prevent IntegrityError
            try:
                self.price = float(self.area_size or 0) * float(self.rate_per_sqft or 0)
            except (TypeError, ValueError):
                self.price = 0.0
            super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.unit_name} - {self.project.name}"


    # -----------------------------
    # LEAD
    # -----------------------------
class Lead(models.Model):

        SOURCE_CHOICES = [
            ('WEBSITE', 'Website'),
            ('SOCIAL', 'Social Media'),
            ('REFERRAL', 'Referral'),
            ('IN_PERSON', 'In Person'),
            ('EMAIL', 'Email'),
            ('CALL', 'Phone Call'),
            ('OTHER', 'Other'),
        ]

        STATUS_CHOICES = [
            ('NEW', 'New'),
            ('ASSIGNED', 'Assigned'),
            ('CONVERTED', 'Converted'),
            ("FORWARDED", "Forwarded"),
            ('LOST', 'Lost'),
        ]

        name = models.CharField(max_length=255)
        email = models.EmailField(blank=True)
        phone = models.CharField(max_length=20)
        whatsapp = models.CharField(max_length=20, blank=True)
        source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
        notes = models.TextField(blank=True)
        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.name


    # ... existing imports ...

    # -----------------------------
    # LEAD UPLOAD HISTORY
    # -----------------------------
class LeadUpload(models.Model):
        file = models.FileField(upload_to='lead_uploads/')
        uploaded_at = models.DateTimeField(auto_now_add=True)
        uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
        status = models.CharField(max_length=20, default='Completed')
        total_leads = models.PositiveIntegerField(default=0)

        def __str__(self):
            return f"Upload {self.id} - {self.uploaded_at.strftime('%Y-%m-%d')}"


    # -----------------------------
    # LEAD ASSIGNMENT
    # -----------------------------
class LeadAssignment(models.Model):
        lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
        assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_leads')
        assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_by')
        assigned_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.lead} → {self.assigned_to.username}"


    # -----------------------------
    # SALE
    # -----------------------------
class Sale(models.Model):

        PAYMENT_METHOD_CHOICES = [
            ('CASH', 'Cash'),
            ('BANK', 'Bank Transfer'),
            ('CHEQUE', 'Cheque'),
            ('ONLINE', 'Online Payment'),
        ]

        PAYMENT_STAGE_CHOICES = [
            ('DOWN', 'Down Payment'),
            ('PARTIAL', 'Partial Payment'),
            ('FULL', 'Full Payment'),
            ('INSTALLMENT', 'Installment'),
            ('OTHER', 'Other'),
        ]

        lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
        project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
        project_unit = models.ForeignKey(ProjectUnit, on_delete=models.SET_NULL, null=True, blank=True)
        sale_amount = models.FloatField()
        quantity = models.PositiveIntegerField(default=1)
        sale_date = models.DateField()
        payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
        payment_stage = models.CharField(max_length=20, choices=PAYMENT_STAGE_CHOICES)
        remarks = models.TextField(blank=True)
        supervised_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_supervised')
        converted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_converted')

        def __str__(self):
            return f"Sale - {self.lead.name}"
