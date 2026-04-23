from django import forms
from .models import Project, ProjectUnit, Lead, Sale
from django.contrib.auth.models import User

# ---------------------
# PROJECT FORM
# ---------------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'launch_date': forms.DateInput(attrs={'type': 'date'})
        }

# ---------------------
# PROJECT UNIT FORM
# ---------------------
class ProjectUnitForm(forms.ModelForm):
    class Meta:
        model = ProjectUnit
        fields = '__all__'

# ---------------------
# LEAD FORM
# ---------------------
from django import forms
from django.contrib.auth.models import User
from .models import Lead

class AssignLeadForm(forms.Form):
    lead = forms.ModelChoiceField(queryset=Lead.objects.none())
    assigned_to = forms.ModelChoiceField(queryset=User.objects.none(), required=False)
    assign_to_self = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lead'].queryset = Lead.objects.filter(status='NEW')


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
# ---------------------
# FORWARD LEAD FORM
# ---------------------
class ForwardLeadForm(forms.Form):
    lead = forms.ModelChoiceField(
        queryset=Lead.objects.filter(status__in=["ASSIGNED", "FORWARDED"]),
        label="Select Lead"
    )

    forward_to = forms.ModelChoiceField(
        # Notice the comma at the end of the queryset line below
        queryset=User.objects.filter(gm_profile__designation__in=["TEAM_LEAD", "BDE"]),
        label="Forward To"
    )

# ---------------------
# SALE FORM
# ---------------------
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        exclude = ['supervised_by', 'converted_by']
        widgets = {
            'sale_date': forms.DateInput(attrs={'type': 'date'})
        }

# ---------------------
# BULK UPLOAD
# ---------------------
class BulkLeadUploadForm(forms.Form):
    file = forms.FileField(
        help_text="Upload CSV or Excel file (.csv, .xlsx)"
    )
    
    
    from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'project_type', 'location', 'description', 'launch_date', 'status']
        widgets = {
            'launch_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }