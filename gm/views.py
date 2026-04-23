from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
import csv
import openpyxl
from django.db import models  # Add this line

from django.shortcuts import render
from django.db.models import Count

# Internal App Imports
from .models import Project, ProjectUnit, Lead, LeadAssignment, Sale
from .forms import ProjectForm, ProjectUnitForm, LeadForm, AssignLeadForm, SaleForm, BulkLeadUploadForm

# Import the custom decorator
# Note: Ensure this utility exists in users/decorators.py or users/utils.py
from users.decorators import role_required 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Sum, Avg, Count
from django.db.models.functions import TruncMonth
import json

from users.models import Profile
from django.contrib.auth.models import User


# Look for this line near the top of gm/views.py
from .models import Project, ProjectUnit, Lead, LeadAssignment, Sale, LeadUpload
#                                                                ^^^^^^^^^^
#                                                                Add this!


from hr.models import Employee  # Add this import at the top
# ---------------------
# DASHBOARD
# ---------------------
@login_required
@role_required("GM")
def gm_dashboard(request):
    # 1. Lead Performance Trend (Last 6 Months)
    lead_trend_data = Lead.objects.annotate(month=TruncMonth('created_at')) \
        .values('month').annotate(count=Count('id')).order_by('month')[:6]
    
    lead_labels = [data['month'].strftime("%b %Y") for data in lead_trend_data]
    lead_counts = [data['count'] for data in lead_trend_data]

    # 2. Monthly Revenue (Last 6 Months)
    revenue_trend_data = Sale.objects.annotate(month=TruncMonth('sale_date')) \
        .values('month').annotate(total=Sum('sale_amount')).order_by('month')[:6]
    
    rev_labels = [data['month'].strftime("%b %Y") for data in revenue_trend_data]
    rev_amounts = [float(data['total']) for data in revenue_trend_data]

    # 3. Project Units (Total vs Sold)
    project_units = Project.objects.annotate(
        total_u=Sum('units__total_units'),
        sold_u=Count('units', filter=models.Q(units__status='SOLD'))
    )
    
    project_names = [p.name for p in project_units]
    total_units_list = [p.total_u or 0 for p in project_units]
    sold_units_list = [p.sold_u or 0 for p in project_units]

    context = {
        'total_projects': Project.objects.count(),
        'total_leads': Lead.objects.count(),
        'converted_leads': Lead.objects.filter(status='CONVERTED').count(),
        'total_sales': Sale.objects.aggregate(Sum('sale_amount'))['sale_amount__sum'] or 0,
        
        # Chart Data (Converted to JSON for JavaScript)
        'lead_labels': json.dumps(lead_labels),
        'lead_counts': json.dumps(lead_counts),
        'rev_labels': json.dumps(rev_labels),
        'rev_amounts': json.dumps(rev_amounts),
        'project_names': json.dumps(project_names),
        'total_units_list': json.dumps(total_units_list),
        'sold_units_list': json.dumps(sold_units_list),
    }
    return render(request, 'gm/dashboard.html', context)


# Required imports at the top of your views.py file:
# from django.db.models import Q
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required

# PROJECTS
# ---------------------
@login_required
@role_required("GM")
def project_list(request):
    projects = Project.objects.all()
    
    # Search and filter functionality
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('project_type', '')
    filter_status = request.GET.get('status', '')
    
    # Apply search filter
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | Q(location__icontains=search_query)
        )
    
    # Apply project type filter
    if filter_type:
        projects = projects.filter(project_type=filter_type)
    
    # Apply status filter
    if filter_status:
        projects = projects.filter(status=filter_status)
    
    # Calculate stats for the boxes
    all_projects = Project.objects.all()
    total_projects = all_projects.count()
    housing_schemes = all_projects.filter(project_type='housing').count()
    shopping_malls = all_projects.filter(project_type='shopping').count()
    commercial = all_projects.filter(project_type='commercial').count()
    
    context = {
        'projects': projects,
        'total_projects': total_projects,
        'housing_schemes': housing_schemes,
        'shopping_malls': shopping_malls,
        'commercial': commercial,
        'search_query': search_query,
        'filter_type': filter_type,
        'filter_status': filter_status,
    }
    
    return render(request, 'gm/projects/project_list.html', context)


from .models import ProjectUnit, Project
@login_required
@role_required("GM")
def project_create(request):
    project_form = ProjectForm(request.POST or None)

    if request.method == "POST":
        if project_form.is_valid():
            # 1. Save the Project first
            project = project_form.save()

            # 2. Extract lists from POST
            unit_names = request.POST.getlist('unit_name[]')
            unit_types = request.POST.getlist('unit_type[]')
            units_count = request.POST.getlist('units[]')
            floors = request.POST.getlist('floor[]')
            area_sizes = request.POST.getlist('area_size[]')
            rates = request.POST.getlist('rate[]')
            commissions = request.POST.getlist('commission[]')
            statuses = request.POST.getlist('unit_status[]')

            # 3. Use zip to iterate through all lists simultaneously
            # This ensures that row 1 of the table maps to one ProjectUnit object
            for name, u_type, count, floor, area, rate, comm, stat in zip(
                unit_names, unit_types, units_count, floors, area_sizes, rates, commissions, statuses
            ):
                # Only save if the name is not empty
                if name.strip():
                    ProjectUnit.objects.create(
                        project=project,
                        unit_name=name.strip(),
                        unit_type=u_type,
                        total_units=int(count) if count else 1,
                        floor=floor,
                        area_size=float(area) if area else 0.0,
                        rate_per_sqft=float(rate) if rate else 0.0,
                        commission_percent=float(comm) if comm else 0.0,
                        status=stat
                    )

            messages.success(request, "Project and units created successfully")
            return redirect('gm:project_list')
        else:
            messages.error(request, "Please correct the errors in the project form.")

    return render(request, 'gm/projects/project_with_units.html', {
        'project_form': project_form,
        'unit_type_choices': ProjectUnit.UNIT_TYPE_CHOICES,
        'floor_choices': ProjectUnit.FLOOR_CHOICES,
        'status_choices': ProjectUnit.STATUS_CHOICES
    })

# ---------------------
# PROJECT UNITS
# ---------------------

@login_required
@role_required("GM")
def unit_create(request):
    form = ProjectUnitForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Project unit added successfully")
            return redirect('gm:project_list')
    
    return render(request, 'gm/projects/unit_form.html', {'form': form})
    

# --- PROJECT DETAIL VIEW ---
@login_required
@role_required("GM")
def project_detail(request, pk):
    # Fetch the project or return 404 if not found
    project = get_object_or_404(Project, pk=pk)
    
    # Get all units related to this project
    units = project.units.all()
    
    return render(request, 'gm/projects/project_detail.html', {
        'project': project,
        'units': units
    })

# --- PROJECT DELETE FUNCTION ---
@login_required
@role_required("GM")
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == "POST":
        project_name = project.name
        project.delete()
        messages.success(request, f"Project '{project_name}' and all its units deleted successfully.")
        return redirect('gm:project_list')
    
    # If it's a GET request, show a confirmation page or redirect
    return render(request, 'gm/projects/project_confirm_delete.html', {'project': project})    
    
    
@login_required
@role_required("GM")
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Using the same ProjectForm you used for creation
    form = ProjectForm(request.POST or None, instance=project)
    
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Project '{project.name}' updated successfully.")
        return redirect('gm:project_list')
    
    return render(request, 'gm/projects/project_form.html', {
        'project_form': form,
        'project': project,
        'is_edit': True
    })    
    
    
@login_required
@role_required("GM")
def project_sales_report(request):
    # Group sales by project and calculate totals
    project_performance = Project.objects.annotate(
        total_revenue=Sum('sale__sale_amount'),
        sales_count=Count('sale')
    ).order_by('-total_revenue')

    # Calculate overall stats for the top cards
    total_projects = Project.objects.count()
    # Find the top performing project by revenue
    top_project = project_performance.first()

    context = {
        'project_performance': project_performance,
        'total_projects': total_projects,
        'top_project': top_project,
    }
    return render(request, "gm/reports/project_sales.html", context)



# ---------------------
# LEADS
# ---------------------
@login_required
@role_required("GM")
def lead_list(request):
    leads = Lead.objects.all().order_by('-created_at') # All leads (including uploaded ones)
    assignments = LeadAssignment.objects.all() # History of assignments
    unassigned_count = Lead.objects.filter(status='NEW').count()
    
    context = {
        'leads': leads,
        'assignments': assignments,
        'unassigned_count': unassigned_count,
    }
    return render(request, 'gm/leads/lead_list.html', context)

@login_required
@role_required("GM")
def lead_create(request):
    form = LeadForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Lead added successfully")
        return redirect('gm:lead_list')
    return render(request, 'gm/leads/lead_form.html', {'form': form})

# ---------------------
# ASSIGN LEADS
# ---------------------


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib.auth import get_user_model
from .models import Lead, LeadAssignment, LeadUpload
from .forms import AssignLeadForm, LeadForm

User = get_user_model()

@login_required
@role_required("GM")
def lead_list(request):
    leads = Lead.objects.all().order_by('-created_at')
    assignments = LeadAssignment.objects.all()
    unassigned_count = Lead.objects.filter(status='NEW').count()
    
    context = {
        'leads': leads,
        'assignments': assignments,
        'unassigned_count': unassigned_count,
    }
    return render(request, 'gm/leads/lead_list.html', context)

@login_required
@role_required("GM")
def assign_lead(request):
    User = get_user_model()

    # Create form FIRST
    form = AssignLeadForm(request.POST or None)

    # ✅ ALWAYS set queryset (CRITICAL)
    form.fields['lead'].queryset = Lead.objects.filter(status='NEW')

    form.fields['assigned_to'].queryset = User.objects.filter(
        gm_profile__designation__icontains='Manager'
    )

    if request.method == "POST":
        if form.is_valid():
            lead = form.cleaned_data["lead"]
            assign_to_self = form.cleaned_data.get("assign_to_self")
            assigned_to = form.cleaned_data.get("assigned_to")

            if assign_to_self:
                assigned_user = request.user
            else:
                if not assigned_to:
                    messages.error(request, "Please select a manager or assign to yourself.")
                    return render(request, "gm/leads/assign_lead.html", {"form": form})
                assigned_user = assigned_to

            # Create assignment
            LeadAssignment.objects.create(
                lead=lead,
                assigned_to=assigned_user,
                assigned_by=request.user
            )

            # Update lead status
            lead.status = "ASSIGNED"
            lead.save()

            messages.success(request, f"Lead '{lead.name}' assigned successfully.")
            return redirect("gm:assigned_leads")

    return render(request, "gm/leads/assign_lead.html", {"form": form})


@login_required
@role_required("GM")
def assigned_leads(request):
    assignments = LeadAssignment.objects.all().order_by('-assigned_at')
    return render(request, 'gm/leads/assigned_leads.html', {'assignments': assignments})


@login_required
@role_required("GM")
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    assignments = LeadAssignment.objects.filter(lead=lead).order_by("-assigned_at")

    context = {
        "lead": lead,
        "assignments": assignments,
    }
    return render(request, "gm/leads/lead_detail.html", context)

# Update your assign_lead view to this single version:
# Update your assign_lead view to this single version:



@login_required
@role_required("MANAGER")
def forward_lead(request):

    # Only leads assigned to THIS manager
    assigned_leads = Lead.objects.filter(
        leadassignment__assigned_to=request.user
    ).distinct()

    form = ForwardLeadForm(request.POST or None)
    form.fields["lead"].queryset = assigned_leads

    if form.is_valid():
        lead = form.cleaned_data["lead"]
        forward_to = form.cleaned_data["forward_to"]

        # Save assignment history
        LeadAssignment.objects.create(
            lead=lead,
            assigned_to=forward_to,
            assigned_by=request.user
        )

        # Update lead status
        lead.status = "FORWARDED"
        lead.save()

        messages.success(
            request,
            f"Lead forwarded to {forward_to.username} successfully."
        )
        return redirect("manager:forward_lead")

    return render(
        request,
        "manager/leads/forward_lead.html",
        {"form": form}
    )
    
    
# gm/views.py

# gm/views.py
from django.db.models import Count, Q
from django.contrib.auth.models import User
# Explicitly import the Profile from the users app to access the 'role' field
from users.models import Profile as UserProfile 
from gm.models import Lead, Sale

# gm/views.py
from django.db.models import Count, Q
from django.contrib.auth.models import User
from users.models import Profile as UserProfile 
from hr.models import Employee  # Import your HR Employee model
from gm.models import Lead, Sale

@login_required
@role_required("GM")
def lead_conversion_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 1. Get all profiles from the users app
    relevant_user_profiles = UserProfile.objects.filter(
        role__in=["GM", "MANAGER", "TEAM_LEAD", "BDE"]
    ).select_related('user')
    
    report_data = []
    total_leads_all = 0
    total_converted_all = 0

    for user_prof in relevant_user_profiles:
        target_user = user_prof.user
        
        # FIND THE NAME: 
        # Check HR Employee model first, then User's full name, then Username
        emp_record = Employee.objects.filter(email=target_user.email).first()
        if emp_record:
            display_name = emp_record.name
        elif target_user.get_full_name():
            display_name = target_user.get_full_name()
        else:
            display_name = target_user.username

        # Leads Logic
        lead_query = Q(leadassignment__assigned_to=target_user)
        if start_date and end_date:
            lead_query &= Q(created_at__date__range=[start_date, end_date])
        total_assigned = Lead.objects.filter(lead_query).distinct().count()

        # Sales Logic
        sale_query = Q(converted_by=target_user)
        if start_date and end_date:
            sale_query &= Q(sale_date__range=[start_date, end_date])
        converted = Sale.objects.filter(sale_query).count()

        rate = (converted / total_assigned * 100) if total_assigned > 0 else 0
        
        total_leads_all += total_assigned
        total_converted_all += converted

        report_data.append({
            'name': display_name,  # This will now show the actual name
            'role': user_prof.role, 
            'total_leads': total_assigned,
            'converted_leads': converted,
            'conversion_rate': round(rate, 1),
            'initial': display_name[0].upper() if display_name else "U",
        })

    avg_rate = (total_converted_all / total_leads_all * 100) if total_leads_all > 0 else 0

    context = {
        'report_data': report_data,
        'total_leads': total_leads_all,
        'converted_leads': total_converted_all,
        'conversion_rate': round(avg_rate, 1),
        'active_employees': relevant_user_profiles.count(),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, "gm/reports/lead_conversion.html", context)


# ---------------------
# SALES
# ---------------------
@login_required
@role_required("GM")
def sale_create(request):
    form = SaleForm(request.POST or None)

    if form.is_valid():
        sale = form.save(commit=False)
        sale.supervised_by = request.user
        sale.converted_by = request.user
        sale.save()

        messages.success(request, "Sale recorded successfully")
        return redirect("gm:sale_list")

    return render(request, "gm/sales/sale_form.html", {"form": form})


@login_required
@role_required("GM")
def sale_list(request):
    sales = Sale.objects.all().order_by("-sale_date")
    return render(request, "gm/sales/sale_list.html", {"sales": sales})

from django.db.models import Sum, Avg, Q

@login_required
@role_required("GM")
def sales_dashboard(request):
    """
    Detailed Sales Dashboard with advanced stats and multi-criteria filters
    """
    sales_qs = Sale.objects.all().select_related('lead', 'project', 'converted_by').order_by("-sale_date")

    # Get Filter Parameters
    query = request.GET.get('q')
    project_id = request.GET.get('project')
    payment_method = request.GET.get('payment_method')
    payment_stage = request.GET.get('payment_stage')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Apply Filters
    if query:
        sales_qs = sales_qs.filter(
            Q(lead__name__icontains=query) | 
            Q(lead__phone__icontains=query) | 
            Q(lead__email__icontains=query)
        )
    if project_id:
        sales_qs = sales_qs.filter(project_id=project_id)
    if payment_method:
        sales_qs = sales_qs.filter(payment_method=payment_method)
    if payment_stage:
        sales_qs = sales_qs.filter(payment_stage=payment_stage)
    if date_from:
        sales_qs = sales_qs.filter(sale_date__gte=date_from)
    if date_to:
        sales_qs = sales_qs.filter(sale_date__lte=date_to)

    # Calculate Stats based on filtered results
    total_sales_count = sales_qs.count()
    total_revenue = sales_qs.aggregate(Sum('sale_amount'))['sale_amount__sum'] or 0
    avg_sale = sales_qs.aggregate(Avg('sale_amount'))['sale_amount__avg'] or 0
    unique_payment_methods = sales_qs.values('payment_method').distinct().count()

    context = {
        'sales': sales_qs,
        'total_sales': total_sales_count,
        'total_revenue': total_revenue,
        'avg_sale': avg_sale,
        'payment_methods_count': unique_payment_methods,
        'projects': Project.objects.all(),
        # Pass choices to template for dropdowns
        'payment_method_choices': Sale.PAYMENT_METHOD_CHOICES,
        'payment_stage_choices': Sale.PAYMENT_STAGE_CHOICES,
    }
    return render(request, "gm/sales/sales_dashboard.html", context)
# gm/views.py
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from users.models import Profile as UserProfile 
from hr.models import Employee  
from gm.models import Sale

@login_required
@role_required("GM")
def sale_summary_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 1. Fetch all User Profiles (GM, Managers, etc.)
    relevant_user_profiles = UserProfile.objects.filter(
        role__in=["GM", "MANAGER", "TEAM_LEAD", "BDE"]
    ).select_related('user')
    
    report_data = []
    grand_total_revenue = 0

    for user_prof in relevant_user_profiles:
        target_user = user_prof.user
        
        # FIND THE NAME: Check HR Employee model first
        emp_record = Employee.objects.filter(email=target_user.email).first()
        display_name = emp_record.name if emp_record else (target_user.get_full_name() or target_user.username)

        # 2. Sale Query for this specific user
        sale_query = Q(converted_by=target_user)
        if start_date and end_date:
            sale_query &= Q(sale_date__range=[start_date, end_date])
        
        # Calculate Total Sales Amount for this user
        user_sales_stats = Sale.objects.filter(sale_query).aggregate(
            total_amt=Sum('sale_amount'),
            total_count=Count('id')
        )
        
        user_total = user_sales_stats['total_amt'] or 0
        user_count = user_sales_stats['total_count'] or 0
        grand_total_revenue += user_total

        report_data.append({
            'name': display_name,
            'role': user_prof.role,
            'total_sales_amount': user_total,
            'sales_count': user_count,
            'initial': display_name[0].upper() if display_name else "U",
        })

    # Sort report_data by highest sales amount
    report_data = sorted(report_data, key=lambda x: x['total_sales_amount'], reverse=True)

    context = {
        'report_data': report_data,
        'grand_total_revenue': grand_total_revenue,
        'active_employees': relevant_user_profiles.count(),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, "gm/reports/sale_summary.html", context)

# ---------------------
# BULK UPLOAD
# ---------------------
@login_required
@role_required("GM")
def bulk_lead_upload(request):
    form = BulkLeadUploadForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST" and form.is_valid():
        upload_file = request.FILES['file']
        ext = upload_file.name.split('.')[-1].lower()
        
        # 1. Create history record
        upload_record = LeadUpload.objects.create(
            file=upload_file,
            uploaded_by=request.user,
            status='Processing'
        )
        
        created_count = 0
        skipped_count = 0
        errors = []
        
        try:
            if ext == 'xlsx':
                wb = openpyxl.load_workbook(upload_file, data_only=True)
                sheet = wb.active
                
                # 2. Get and clean headers from Row 1
                headers = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
                
                # 3. Process rows starting from Row 2
                for row_idx, row_values in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    # Skip completely empty rows
                    if not any(row_values):
                        continue
                        
                    data = dict(zip(headers, row_values))
                    
                    # 4. Extract data using your exact column names
                    name = data.get('Name') or 'Unknown'
                    email = data.get('Email') or ''
                    phone = str(data.get('Phone')).strip() if data.get('Phone') else None
                    whatsapp = str(data.get('Whatsapp')).strip() if data.get('Whatsapp') else ''
                    source_raw = str(data.get('Source') or 'OTHER').upper().replace(" ", "_")
                    notes = data.get('Notes') or ''
                    status_raw = str(data.get('Status') or 'NEW').upper()

                    # 5. Validation Check
                    if not phone or phone == 'None':
                        errors.append(f"Row {row_idx}: Missing Phone Number.")
                        skipped_count += 1
                        continue
                    
                    if Lead.objects.filter(phone=phone).exists():
                        errors.append(f"Row {row_idx}: Phone {phone} already exists in Leads.")
                        skipped_count += 1
                        continue

                    # 6. Save to Lead Table
                    Lead.objects.create(
                        name=name,
                        email=email,
                        phone=phone,
                        whatsapp=whatsapp,
                        source=source_raw,
                        notes=notes,
                        status=status_raw
                    )
                    created_count += 1

                # 7. Finalize History Record
                upload_record.status = 'Completed'
                upload_record.total_leads = created_count
                upload_record.save()

                # 8. Success/Error Feedback
                if created_count > 0:
                    messages.success(request, f"Successfully added {created_count} leads.")
                if errors:
                    # Show the first 3 errors so you know what's wrong
                    for err in errors[:3]:
                        messages.warning(request, err)
                
                return redirect('gm:lead_list')

            else:
                messages.error(request, "Please upload a valid .xlsx file.")
                
        except Exception as e:
            upload_record.status = 'Failed'
            upload_record.save()
            messages.error(request, f"System Error: {str(e)}")
            
    return render(request, 'gm/leads/bulk_upload.html', {'form': form})


# --- USER MANAGEMENT VIEWS ---
# Helper function to link User emails to HR Names
def get_hr_name_map():
    hr_employees = Employee.objects.all()
    # Maps email to name from the HR Directory
    return {emp.email: emp.name for emp in hr_employees if emp.email}

# gm/views.py - Updated Assignment Views
@login_required
@role_required("GM")
def manager_assign(request):
    """GM assigns Managers: Shows all HR Managers and allows assignment to GMs"""
    gm_employees = Employee.objects.filter(designation__iexact='GM', status='Active')
    manager_employees = Employee.objects.filter(designation__iexact='Manager', status='Active')
    
    # Map email to HR name for all potential managers
    hr_name_map = {emp.email: emp.name for emp in manager_employees if emp.email}
    
    gms_list = []
    for emp in gm_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            assigned_profiles = Profile.objects.filter(reporting_to=user, designation='Manager')
            
            # ATTACH HR NAME TO PROFILE OBJECTS
            for profile in assigned_profiles:
                profile.hr_name = hr_name_map.get(profile.user.email, profile.user.username)

            gms_list.append({
                'id': user.id,
                'hr_name': emp.name,
                'emp_id': emp.emp_id,
                'assigned_managers': assigned_profiles,
                'assigned_count': assigned_profiles.count()
            })

    available_managers = []
    for emp in manager_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            profile, _ = Profile.objects.get_or_create(user=user, defaults={'designation': 'Manager'})
            available_managers.append({
                'id': user.id,
                'hr_name': emp.name,
                'emp_id': emp.emp_id,
                'reporting_to_id': profile.reporting_to_id
            })

    if request.method == "POST":
        gm_id = request.POST.get('gm_id')
        manager_ids = request.POST.getlist('manager_ids')
        if gm_id and manager_ids:
            Profile.objects.filter(user_id__in=manager_ids).update(reporting_to_id=gm_id, designation='Manager')
            messages.success(request, f"Successfully assigned {len(manager_ids)} managers.")
            return redirect('gm:manager_assign')

    return render(request, "gm/users/manager_assign.html", {"gms": gms_list, "managers": available_managers})
@login_required
@role_required("GM")
def team_lead_assign(request):
    """Manager assigns Team Leads"""
    mgr_employees = Employee.objects.filter(designation__iexact='Manager', status='Active')
    tl_employees = Employee.objects.filter(designation__in=['Team Leader', 'Team Lead'], status='Active')
    
    # Map email to HR name for all potential Team Leads (to look up names for the badges)
    hr_name_map = {emp.email: emp.name for emp in tl_employees if emp.email}

    managers_list = []
    for emp in mgr_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            assigned_tls = Profile.objects.filter(reporting_to=user, designation='TEAM_LEAD')
            
            # ATTACH HR NAME TO EACH PROFILE
            for profile in assigned_tls:
                profile.hr_name = hr_name_map.get(profile.user.email, profile.user.username)
                
            managers_list.append({
                'id': user.id, 
                'hr_name': emp.name, 
                'emp_id': emp.emp_id,
                'assigned_tls': assigned_tls,
                'assigned_count': assigned_tls.count() # Critical for the "Unassigned" check
            })

    tls_list = []
    for emp in tl_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            profile, _ = Profile.objects.get_or_create(user=user, defaults={'designation': 'TEAM_LEAD'})
            tls_list.append({
                'id': user.id, 
                'hr_name': emp.name, 
                'emp_id': emp.emp_id,
                'reporting_to_id': profile.reporting_to_id
            })

    if request.method == "POST":
        mgr_id = request.POST.get('manager_id')
        tl_ids = request.POST.getlist('tl_ids')
        Profile.objects.filter(user_id__in=tl_ids).update(reporting_to_id=mgr_id, designation='TEAM_LEAD')
        messages.success(request, "Team Leads assigned successfully.")
        return redirect('gm:team_lead_assign')

    return render(request, "gm/users/team_lead_assign.html", {"managers": managers_list, "team_leads": tls_list})

@login_required
@role_required("GM")
def bde_assign(request):
    """Team Lead assigns BDEs"""
    tl_employees = Employee.objects.filter(designation__in=['Team Leader', 'Team Lead'], status='Active')
    bde_employees = Employee.objects.filter(designation__iexact='BDE', status='Active')
    
    # Map email to HR name for all potential BDEs
    hr_name_map = {emp.email: emp.name for emp in bde_employees if emp.email}

    tls_list = []
    for emp in tl_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            assigned_bdes = Profile.objects.filter(reporting_to=user, designation='BDE')
            
            # ATTACH HR NAME TO EACH PROFILE
            for profile in assigned_bdes:
                profile.hr_name = hr_name_map.get(profile.user.email, profile.user.username)
                
            tls_list.append({
                'id': user.id, 
                'hr_name': emp.name, 
                'emp_id': emp.emp_id,
                'assigned_bdes': assigned_bdes,
                'assigned_count': assigned_bdes.count() # Critical for the "Unassigned" check
            })

    bdes_list = []
    for emp in bde_employees:
        user = User.objects.filter(email=emp.email).first()
        if user:
            profile, _ = Profile.objects.get_or_create(user=user, defaults={'designation': 'BDE'})
            bdes_list.append({
                'id': user.id, 
                'hr_name': emp.name, 
                'emp_id': emp.emp_id,
                'reporting_to_id': profile.reporting_to_id
            })

    if request.method == "POST":
        tl_id = request.POST.get('tl_id')
        bde_ids = request.POST.getlist('bde_ids')
        Profile.objects.filter(user_id__in=bde_ids).update(reporting_to_id=tl_id, designation='BDE')
        messages.success(request, "BDEs assigned successfully.")
        return redirect('gm:bde_assign')

    return render(request, "gm/users/bde_assign.html", {"team_leads": tls_list, "bdes": bdes_list})
    
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile  # Ensure Profile is imported

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile

def manager_assign_view(request):
    if request.method == 'POST':
        gm_id = request.POST.get('gm_id')
        manager_ids = request.POST.getlist('manager_ids')
        
        gm_user = get_object_or_404(User, id=gm_id)
        
        # Reset current assignments for this GM to avoid duplicates if needed
        # Or simply update the selected ones:
        for m_id in manager_ids:
            manager_user = User.objects.get(id=m_id)
            profile, created = Profile.objects.get_or_create(user=manager_user)
            profile.reporting_to = gm_user
            profile.designation = "Manager" # Keep consistent casing
            profile.save()
            
        return redirect('gm:manager_assign')

    # FIX: Changed 'role' to 'designation' here
    # Use 'gm_profile' because of the related_name we set earlier
    gms = User.objects.filter(gm_profile__designation="GM")
    managers = User.objects.filter(gm_profile__designation="Manager")
    
    return render(request, 'gm/users/manager_assign.html', {
        'gms': gms,
        'managers': managers
    })