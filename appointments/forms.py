from django import forms
from .models import Appointment, Consultation
from users.models import User
from patients.models import Patient

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient','doctor','appointment_type','date','time','reason','fee','notes']
        widgets = {
            'date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'time': forms.TimeInput(attrs={'type':'time','class':'form-control'}),
            'reason': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2,'class':'form-control'}),
            'fee': forms.NumberInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        for f in self.fields.values():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'form-select'
        if user and user.role == 'patient':
            self.fields.pop('patient', None)

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['patient','doctor','chief_complaint','diagnosis','treatment_plan','status','fee','follow_up_date','notes']
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
            'diagnosis': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
            'treatment_plan': forms.Textarea(attrs={'rows':3,'class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2,'class':'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'fee': forms.NumberInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role='doctor')
        for f in self.fields.values():
            if not f.widget.attrs.get('class'):
                f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select):
                f.widget.attrs['class'] = 'form-select'
        if user and user.role == 'patient':
            self.fields.pop('patient', None)
            self.fields.pop('diagnosis', None)
            self.fields.pop('treatment_plan', None)
            self.fields.pop('status', None)
