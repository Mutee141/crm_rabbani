from django.urls import path
from . import views

app_name = 'teamlead'

urlpatterns = [
    path('dashboard/', views.team_lead_dashboard, name='dashboard'),
    path('assign-leads/', views.assign_leads_to_bde, name='assign_leads'),
    path('assignment-history/', views.assignment_history, name='assignment_history'),
    path('self-feedback/', views.self_feedback, name='self_feedback'),
]