from django import forms
from .models import Bill, BillItem

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['patient','due_date','discount','tax','notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'notes': forms.Textarea(attrs={'rows':2,'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if not f.widget.attrs.get('class'): f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select): f.widget.attrs['class'] = 'form-select'

class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['item_type','description','quantity','unit_price']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            if not f.widget.attrs.get('class'): f.widget.attrs['class'] = 'form-control'
            if isinstance(f.widget, forms.Select): f.widget.attrs['class'] = 'form-select'
