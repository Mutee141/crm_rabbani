from django.urls import path
from . import views

app_name = "gm"

urlpatterns = [
    path("", views.gm_dashboard, name="dashboard"),
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("reports/project-sales/", views.project_sales_report, name="project_sales_report"),
    path("units/create/", views.unit_create, name="unit_create"),
    # ... existing paths ...
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    path("leads/", views.lead_list, name="lead_list"),
    path("leads/create/", views.lead_create, name="lead_create"),
    path("leads/assign/", views.assign_lead, name="assign_lead"),
    path("leads/assigned/", views.assigned_leads, name="assigned_leads"),
    
    path("leads/bulk-upload/", views.bulk_lead_upload, name="bulk_lead_upload"),
    path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
    path("forward-lead/", views.forward_lead, name="forward_lead"),
    path("reports/conversion/", views.lead_conversion_report, name="lead_conversion_report"),
    
    path("sales/dashboard/", views.sales_dashboard, name="sales_dashboard"),
    path("sales/", views.sale_list, name="sale_list"),
    path("sales/add/", views.sale_create, name="sale_create"),
    path("reports/sale-summary/", views.sale_summary_report, name="sale_summary_report"),


    # User Management
    path("manage/managers/", views.manager_assign, name="manager_assign"),
    path("manage/team-leads/", views.team_lead_assign, name="team_lead_assign"),
    path("manage/bdes/", views.bde_assign, name="bde_assign"),
    
]

