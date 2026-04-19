from django import forms
from .models import Patient, MedicalRecord, Vitals, LabResult

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name','age','gender','phone','address','blood_type','status','emergency_contact','emergency_phone','allergies','assigned_doctor','notes']
        widgets = {f: forms.TextInput(attrs={'class':'form-control'}) for f in ['name','age','phone','address','blood_type','emergency_contact','emergency_phone']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
        self.fields['notes'].widget = forms.Textarea(attrs={'class':'form-control','rows':3})
        self.fields['allergies'].widget = forms.Textarea(attrs={'class':'form-control','rows':2})

class VitalsForm(forms.ModelForm):
    class Meta:
        model = Vitals
        fields = ['temperature','blood_pressure','pulse','weight','height','oxygen_saturation','notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis','symptoms','treatment','notes']
        widgets = {f: forms.Textarea(attrs={'class':'form-control','rows':3}) for f in ['diagnosis','symptoms','treatment','notes']}

class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = ['test_name','result','reference_range','status','file','notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'
        self.fields['status'].widget.attrs['class'] = 'form-select'
