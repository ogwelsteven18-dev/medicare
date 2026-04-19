from django import forms
from .models import Medicine, Prescription, MedicineOrder

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name','generic_name','category','manufacturer','unit_price','stock_quantity','reorder_level','description']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select): f.widget.attrs['class'] = 'form-select'

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient','notes']
        widgets = {'notes': forms.Textarea(attrs={'rows':2,'class':'form-control'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if not f.widget.attrs.get('class'): f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select): f.widget.attrs['class'] = 'form-select'

class MedicineOrderForm(forms.ModelForm):
    class Meta:
        model = MedicineOrder
        fields = ['patient','notes']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if not f.widget.attrs.get('class'): f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select): f.widget.attrs['class'] = 'form-select'
