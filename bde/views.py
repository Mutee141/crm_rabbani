from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from gm.models import Lead, LeadAssignment, Sale

@role_required("BDE")
def bde_dashboard(request):
    """BDE Overview: Stats for leads assigned to them"""
    my_leads = LeadAssignment.objects.filter(assigned_to=request.user)
    
    total_leads = my_leads.count()
    conversions = Sale.objects.filter(converted_by=request.user).count()
    
    # Pre-calculate conversion rate to avoid template math errors
    conversion_rate = 0
    if total_leads > 0:
        conversion_rate = round((conversions / total_leads) * 100, 1)
    
    context = {
        "total_leads": total_leads,
        "conversions": conversions,
        "conversion_rate": conversion_rate,
        "revenue": 0, 
    }
    return render(request, "bde/dashboard.html", context)

# bde/views.py

@login_required
@role_required("BDE")
def bde_assigned_leads(request):
    # We fetch the Lead (for name/status) and the User who assigned it
    leads = LeadAssignment.objects.filter(
        assigned_to=request.user
    ).select_related('lead', 'assigned_by').order_by('-assigned_at')
    
    return render(request, "bde/assigned_leads.html", {"leads": leads})


@role_required("BDE")
def bde_self_feedback(request):
    pending_leads = LeadAssignment.objects.filter(
        assigned_to=request.user, 
        lead__status='PENDING'
    ).select_related('lead')
    
    return render(request, "bde/self_feedback.html", {
        "leads": pending_leads,
        "pending_count": pending_leads.count()
    })