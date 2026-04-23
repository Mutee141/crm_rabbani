from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from users.decorators import role_required
from gm.models import Lead, LeadAssignment, Sale, Project, ProjectUnit

from users.models import Profile
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta

@role_required("MANAGER")
def manager_dashboard(request):
    # ... (Keep your existing code) ...
    
    # --- CHART DATA CALCULATION ---
    today = timezone.now().date()
    days = []
    leads_data = []
    conversions_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days.append(day.strftime('%a'))  # Sun, Mon, etc.
        
        # Leads assigned on this day to this manager's team
        daily_leads = LeadAssignment.objects.filter(
            assigned_to=request.user, 
            assigned_at__date=day
        ).count()
        leads_data.append(daily_leads)
        
        # Conversions (Sales) supervised by this manager on this day
        daily_conversions = Sale.objects.filter(
            supervised_by=request.user, 
            sale_date=day
        ).count()
        conversions_data.append(daily_conversions)

    context = {
        # ... (Your existing context) ...
        "chart_labels": days,
        "chart_leads": leads_data,
        "chart_conversions": conversions_data,
    }
    return render(request, "manager/dashboard.html", context)



@role_required("MANAGER")
def assign_leads(request):
    """Allows Manager to distribute leads received from GM to Team Leads or keep for self."""
    # 1. Fetch leads assigned to this manager
    assignments = LeadAssignment.objects.filter(assigned_to=request.user).select_related('lead')
    
    # 2. FIXED QUERY: Get Profiles where reporting_to is this manager AND role is TEAM_LEAD
    # We query the Profile model because that's where 'role' and 'reporting_to' live
    team_lead_profiles = Profile.objects.filter(
        reporting_to=request.user, 
        role='TEAM_LEAD'
    ).select_related('user')

    if request.method == "POST":
        selected_lead_ids = request.POST.getlist('selected_leads')
        assign_to_id = request.POST.get('assign_to') # This will be a User ID
        remarks = request.POST.get('remarks', '')

        if not selected_lead_ids:
            messages.error(request, "Please select at least one lead.")
        else:
            if assign_to_id != "self":
                for lead_id in selected_lead_ids:
                    assignment = LeadAssignment.objects.filter(
                        lead_id=lead_id, 
                        assigned_to=request.user
                    ).first()
                    
                    if assignment:
                        # Re-assign to the selected User ID
                        assignment.assigned_to_id = assign_to_id
                        assignment.assigned_by = request.user
                        assignment.save()
                        
                        # Update lead notes
                        lead = assignment.lead
                        lead.notes = (lead.notes or "") + f"\nManager Remarks: {remarks}"
                        lead.save()
                messages.success(request, f"Successfully assigned {len(selected_lead_ids)} leads.")
            else:
                messages.info(request, "Leads kept for self-management.")
            
            return redirect('manager:assign_leads')

    return render(request, "manager/assign_leads.html", {
        "assignments": assignments,
        "team_leads": team_lead_profiles  # Passing profiles instead of User queryset
    })

# manager/views.py
from django.db.models import Q
from gm.models import LeadAssignment

@role_required("MANAGER")
def assigned_leads(request):
    """
    Shows history of all leads processed or pushed down by this Manager.
    """
    # We use select_related to pull lead and assigned_to info in one go
    # This ensures that even if the 'assigned_by' changes later, 
    # we track the history correctly.
    history = LeadAssignment.objects.filter(
        assigned_by=request.user
    ).select_related('lead', 'assigned_to').order_by('-assigned_at')
    
    return render(request, "manager/assigned_leads.html", {
        "assigned_leads": history
    })

@role_required("MANAGER")
def self_feedback(request):
    """
    Shows leads the manager assigned to themselves to provide updates.
    """
    self_assignments = LeadAssignment.objects.filter(
        assigned_to=request.user, 
        lead__status='ASSIGNED'
    ).select_related('lead')
    
    return render(request, "manager/self_feedback.html", {
        "self_assignments": self_assignments
    })

@role_required("MANAGER")
def sale_entry(request):
    """
    Allows the Manager to create a Sale record for leads marked as CONVERTED.
    """
    converted_leads = Lead.objects.filter(status='CONVERTED', sale__isnull=True)
    projects = Project.objects.all()
    units = ProjectUnit.objects.filter(status='AVAILABLE')
    
    if request.method == "POST":
        lead_id = request.POST.get('lead_id')
        lead = get_object_or_404(Lead, id=lead_id)
        
        Sale.objects.create(
            lead=lead,
            project_id=request.POST.get('project'),
            project_unit_id=request.POST.get('unit'),
            sale_amount=request.POST.get('amount'),
            quantity=request.POST.get('quantity', 1),
            sale_date=request.POST.get('date'),
            payment_method=request.POST.get('method'),
            payment_stage=request.POST.get('stage'),
            remarks=request.POST.get('remarks'),
            supervised_by=request.user,
            converted_by=request.user 
        )
        messages.success(request, f"Sale recorded successfully for {lead.name}!")
        return redirect('manager:sale_entry')

    return render(request, "manager/sale_entry.html", {
        "converted_leads": converted_leads,
        "projects": projects,
        "units": units
    })

@role_required("MANAGER")
def sale_summary_report(request):
    """
    A list of all sales supervised by this manager. 
    Shows sales entered by both the GM and this Manager.
    """
    sales = Sale.objects.filter(supervised_by=request.user).select_related(
        'lead', 'project', 'project_unit', 'converted_by'
    ).order_by('-sale_date')
    return render(request, "manager/reports/sale_summary.html", {"sales": sales})