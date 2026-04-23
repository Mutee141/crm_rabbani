from django.urls import path
from . import views

app_name = 'hr'
urlpatterns = [
    path("", views.hr_dashboard, name="hr_dashboard"),

    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/edit/<int:pk>/", views.employee_update, name="employee_update"),
    path("employees/delete/<int:pk>/", views.employee_delete, name="employee_delete"),

    path("leaves/", views.leave_list, name="leave_list"),
    path("leaves/add/", views.leave_create, name="leave_create"),
    path("leaves/edit/<int:pk>/", views.leave_update, name="leave_update"),
    path("leaves/delete/<int:pk>/", views.leave_delete, name="leave_delete"),

   # Attendance Upload
    path("attendance/upload/", views.attendance_upload, name="attendance_upload"),
    path("attendance/upload/delete/<int:pk>/", views.attendance_upload_delete, name="attendance_upload_delete"),

    # Attendance Schedules (Renamed to match template)
    path("attendance/schedules/", views.schedule_list, name="attendance_schedule_list"),
    path("attendance/schedules/add/", views.schedule_create, name="attendance_schedule_create"), # CHANGED
    path("attendance/schedules/edit/<int:schedule_id>/", views.schedule_edit, name="attendance_schedule_edit"), # CHANGED
    path("attendance/schedules/delete/<int:schedule_id>/", views.schedule_delete, name="attendance_schedule_delete"), # CHANGED
    
    # Records & Generation
    path("attendance/latest/", views.latest_attendance, name="attendance_latest"),
    path("attendance/generate/", views.generate_attendance, name="attendance_generate"),
    path("attendance/record/add/", views.attendance_record_create, name="attendance_record_create"),
    path("attendance/record/edit/<int:pk>/", views.attendance_record_edit, name="attendance_record_edit"),
    # Ensure this exactly says <int:schedule_id>
    path("attendance/schedules/edit/<int:schedule_id>/", views.schedule_edit, name="attendance_schedule_edit"),
    path("attendance/schedules/delete/<int:schedule_id>/", views.schedule_delete, name="attendance_schedule_delete"),

    path("reports/attendance/", views.attendance_report, name="attendance_report"),
    path("reports/attendance/excel/", views.attendance_report_excel, name="attendance_report_excel"),
    path("reports/attendance/pdf/", views.attendance_report_pdf, name="attendance_report_pdf"),
    path("reports/monthly-summary/", views.monthly_summary_report, name="monthly_summary_report"),
    path("reports/department-stats/", views.department_stats_report, name="department_stats_report"),
]
