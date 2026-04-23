from django.contrib import admin
from .models import Employee, Leave
from django.contrib import admin
from .models import (
    Employee,
    Leave,
    AttendanceUpload,
    AttendanceSchedule,
    AttendanceRecord,
    Record,
    
)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("emp_id","name","designation","department","status","date_of_joining")
    search_fields = ("name","emp_id","cnic_no","email")
    list_filter = ("designation","department","status")


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ("employee","leave_type","date","created_at")
    search_fields = ("employee__name","employee__emp_id")
    list_filter = ("leave_type","date")

@admin.register(AttendanceUpload)
class AttendanceUploadAdmin(admin.ModelAdmin):
    list_display = ("file", "uploaded_at", "status")
    list_filter = ("status",)


@admin.register(AttendanceSchedule)
class AttendanceScheduleAdmin(admin.ModelAdmin):
    list_display = ("name", "schedule_type", "check_in_time", "check_out_time", "is_active")
    list_filter = ("schedule_type", "is_active")



@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "check_in",
        "check_out",
        "status",
    )
    list_filter = ("date", "status")
    search_fields = ("employee__name", "employee__emp_id") 




@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "date",
        "check_in",
        "check_out",
        
    )