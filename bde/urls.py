from django.urls import path
from . import views

app_name = 'bde'

urlpatterns = [
    path('dashboard/', views.bde_dashboard, name='dashboard'),
    path('assigned-leads/', views.bde_assigned_leads, name='assigned_leads'),
    path('self-feedback/', views.bde_self_feedback, name='self_feedback'),
]