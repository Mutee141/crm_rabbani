from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Employee,
    Leave,
    AttendanceUpload,
    AttendanceSchedule,
    AttendanceRecord
)

# ------------------------
# File Size Validation
# ------------------------
def validate_file_size(file):
    max_mb = 10
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Max file size is {max_mb}MB")


# ------------------------
# Employee Form
# ------------------------
class EmployeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply professional styling to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control custom-input',
                'placeholder': f'Enter {field.label}'
            })

    date_of_joining = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), 
        required=False
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}), 
        required=False
    )
    profile_image = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False
    )

    class Meta:
        model = Employee
        fields = "__all__"


# ------------------------
# Leave Form
# ------------------------
# ... (rest of your imports and EmployeeForm stay the same)

# ------------------------
# Leave Form
# ------------------------
class LeaveForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    attachment = forms.FileField(required=False)

    class Meta:
        model = Leave
        fields = ["employee", "leave_type", "date", "reason", "attachment"]

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if not attachment:
            return attachment

        # Check size (works for both new and existing files)
        validate_file_size(attachment)

        # FIX: Check if this is a NEW upload (has content_type)
        if hasattr(attachment, 'content_type'):
            allowed = ["application/pdf", "image/jpeg", "image/png"]
            if attachment.content_type not in allowed:
                raise ValidationError("Only PDF, JPG, PNG allowed")
        
        return attachment

# REMOVE the second clean_attachment function that was floating outside the class!

   
# ------------------------
# Attendance Schedule Form
# ------------------------
class AttendanceScheduleForm(forms.ModelForm):
    class Meta:
        model = AttendanceSchedule
        fields = "__all__"
        widgets = {
            "check_in_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time", "class": "form-control"}
            ),
            "check_out_time": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time", "class": "form-control"}
            ),
        }


# ------------------------
# Attendance Upload Form
# ------------------------
from django import forms
from django.core.exceptions import ValidationError
import os

class AttendanceUploadForm(forms.ModelForm):
    class Meta:
        model = AttendanceUpload
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get("file")

        if not file:
            raise ValidationError("No file selected.")

        ext = os.path.splitext(file.name)[1].lower()

        if ext != ".xlsx":
            raise ValidationError("Only XLSX files are supported.")

        return file


# ------------------------
# Attendance Record Form
# ------------------------
class AttendanceRecordForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    check_in = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}), required=False)
    check_out = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}), required=False)

    class Meta:
        model = AttendanceRecord
        fields = "__all__"
    