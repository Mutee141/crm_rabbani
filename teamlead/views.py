from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from gm.models import Lead, LeadAssignment, Sale


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.decorators import role_required
from gm.models import Lead, LeadAssignment, Sale

# ADD THESE IMPORTS TO FIX THE ERROR
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncDate
import json

from django.db.models import Count, Q

@login_required
@role_required("TEAM_LEAD")
def team_lead_dashboard(request):
    """Overview of team performance and lead stats with charts"""
    
    # 1. Standard Stats Logic
    my_leads_count = LeadAssignment.objects.filter(assigned_to=request.user).count()
    
    team_sales = Sale.objects.filter(
        Q(converted_by=request.user) | Q(converted_by__profile__reporting_to=request.user)
    )
    
    sales_count = team_sales.count()
    total_revenue = team_sales.aggregate(total=Sum('sale_amount'))['total'] or 0
    
    conversion_rate = 0
    if my_leads_count > 0:
        conversion_rate = round((sales_count / my_leads_count) * 100, 1)

    # 2. Chart 1: Status Distribution (Doughnut Chart)
    # We fetch leads assigned to this TL and count them by status
    status_data = Lead.objects.filter(
        leadassignment__assigned_to=request.user
    ).values('status').annotate(count=Count('id'))
    
    status_labels = [s['status'] for s in status_data]
    status_counts = [s['count'] for s in status_data]

    # 3. Chart 2: Weekly Performance (Bar Chart)
    # Shows lead assignments for the last 7 days
    performance_data = LeadAssignment.objects.filter(
        assigned_to=request.user
    ).annotate(date=TruncDate('assigned_at')).values('date').annotate(count=Count('id')).order_by('date')[:7]
    
    perf_labels = [p['date'].strftime("%a") for p in performance_data]
    perf_counts = [p['count'] for p in performance_data]

    context = {
        "total_leads": my_leads_count,
        "converted": sales_count,
        "revenue": f"{total_revenue:,}",
        "conversion_rate": conversion_rate,
        # JSON serialized data for JavaScript
        "status_labels": json.dumps(status_labels),
        "status_counts": json.dumps(status_counts),
        "perf_labels": json.dumps(perf_labels),
        "perf_counts": json.dumps(perf_counts),
    }
    return render(request, "teamlead/dashboard.html", context)

# teamlead/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import Profile as UserProfile  # Import the correct Profile model
from gm.models import LeadAssignment

@role_required("TEAM_LEAD")
def assign_leads_to_bde(request):
    """Assign leads from TL's bucket to their BDEs"""
    # 1. Get leads currently assigned to this Team Lead
    my_assignments = LeadAssignment.objects.filter(assigned_to=request.user).select_related('lead')

    # 2. FIX: Fetch BDEs who report to this Team Lead
    # We query UserProfile because that's where 'role' and 'reporting_to' usually live
    bde_profiles = UserProfile.objects.filter(
        reporting_to=request.user, 
        role='BDE'
    ).select_related('user')
    
    # Extract the actual user objects from the profiles
    my_bdes = [profile.user for profile in bde_profiles]

    if request.method == "POST":
        selected_lead_ids = request.POST.getlist('selected_leads')
        assign_to_id = request.POST.get('assign_to')

        if selected_lead_ids:
            if assign_to_id != "self":
                for lead_id in selected_lead_ids:
                    assignment = LeadAssignment.objects.filter(
                        lead_id=lead_id, 
                        assigned_to=request.user
                    ).first()
                    
                    if assignment:
                        assignment.assigned_to_id = assign_to_id
                        assignment.assigned_by = request.user
                        assignment.save()
                messages.success(request, f"Assigned {len(selected_lead_ids)} leads successfully.")
            else:
                messages.info(request, "Leads kept for self-management.")
            return redirect('teamlead:assign_leads')

    return render(request, "teamlead/assign_leads.html", {
        "assignments": my_assignments,
        "bdes": my_bdes # Now passing a list of User objects
    })

@login_required
@role_required("TEAM_LEAD")
def assignment_history(request):
    # Get all assignments for this Team Lead's team
    history = LeadAssignment.objects.filter(assigned_to__profile__reporting_to=request.user).order_by('-assigned_at')
    
    # Calculate counts
    total_assigned = history.count()
    
    # Leads with feedback (assuming feedback is stored in Lead.notes or a Feedback model)
    # Adjust 'notes__isnull=False' based on your actual model field
    leads_with_feedback = history.exclude(Q(lead__notes="") | Q(lead__notes__isnull=True)).count()
    
    # Converted Sales
    converted_sales = history.filter(lead__status='CONVERTED').count()

    context = {
        'history': history,
        'total_assigned': total_assigned,
        'leads_with_feedback': leads_with_feedback,
        'converted_sales': converted_sales,
    }
    return render(request, "teamlead/assigned_leads.html", context)

@role_required("TEAM_LEAD")
def self_feedback(request):
    """Handle feedback for leads the Team Lead is working on personally"""
    # Changed 'status' to 'lead__status' since status belongs to the Lead model
    self_assigned_leads = LeadAssignment.objects.filter(
        assigned_to=request.user,
        lead__status='PENDING' 
    ).select_related('lead')

    pending_count = self_assigned_leads.count()

    context = {
        "leads": self_assigned_leads,
        "pending_count": pending_count,
    }
    return render(request, "teamlead/self_feedback.html", context)