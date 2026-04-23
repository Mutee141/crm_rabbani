from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Project,
    ProjectUnit,
    Lead,
    LeadAssignment,
    Sale
)

# -------------------------
# PROJECT UNIT INLINE
# -------------------------
class ProjectUnitInline(admin.TabularInline):
    model = ProjectUnit
    extra = 1


# -------------------------
# PROJECT ADMIN
# -------------------------
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_type', 'location', 'status', 'launch_date')
    list_filter = ('project_type', 'status')
    search_fields = ('name', 'location')
    inlines = [ProjectUnitInline]


# -------------------------
# PROJECT UNIT ADMIN
# -------------------------
@admin.register(ProjectUnit)
class ProjectUnitAdmin(admin.ModelAdmin):
    list_display = (
        'unit_name',
        'project',
        'unit_type',
        'floor',
        'area_size',
        'rate_per_sqft',
        'price',
        'status'
    )
    list_filter = ('unit_type', 'floor', 'status')
    search_fields = ('unit_name', 'project__name')
    readonly_fields = ('price',)


# -------------------------
# LEAD ADMIN
# -------------------------
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'source', 'status', 'created_at')
    list_filter = ('source', 'status')
    search_fields = ('name', 'phone', 'email')
    ordering = ('-created_at',)


# ... existing imports ...
from .models import LeadUpload

@admin.register(LeadUpload)
class LeadUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'uploaded_at', 'uploaded_by', 'total_leads', 'status')
    list_filter = ('status', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'total_leads', 'status')

    # This makes the admin look like your professional screenshot
    def has_add_permission(self, request):
        return True

# -------------------------
# LEAD ASSIGNMENT ADMIN
# -------------------------
@admin.register(LeadAssignment)
class LeadAssignmentAdmin(admin.ModelAdmin):
    list_display = ('lead', 'assigned_to', 'assigned_by', 'assigned_at')
    list_filter = ('assigned_to', 'assigned_by')
    search_fields = ('lead__name', 'assigned_to__username')


# -------------------------
# SALE ADMIN
# -------------------------
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'lead',
        'project',
        'project_unit',
        'sale_amount',
        'sale_date',
        'payment_method',
        'payment_stage',
        'supervised_by',
        'converted_by'
    )
    list_filter = ('payment_method', 'payment_stage', 'sale_date')
    search_fields = ('lead__name',)



