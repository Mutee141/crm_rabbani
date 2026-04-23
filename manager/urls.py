from django.urls import path
from . import views

app_name = 'manager'

urlpatterns = [
    # Main Manager Dashboard
    path('', views.manager_dashboard, name='dashboard'),
    
    # Placeholder paths for the links seen in your screenshot
    # You can create these views as you build the features
    path('assign-leads/', views.assign_leads, name='assign_leads'),
    path('assigned-leads/', views.assigned_leads, name='assigned_leads'),
    path('self-feedback/', views.self_feedback, name='self_feedback'),
    path('sale-entry/', views.sale_entry, name='sale_entry'),
    
    # Reports section
    path('reports/sale-summary/', views.sale_summary_report, name='sale_summary_report'),
]