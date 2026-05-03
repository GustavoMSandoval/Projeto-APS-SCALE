from django import forms
from core.models import EmergyReference

class EmergyReferenceForm(forms.ModelForm):
    class Meta:
        model = EmergyReference
        fields = ['resource_name', 'unit', 'uev_value', 'source', 'category']
        labels = {
            'resource_name': 'Recurso',
            'unit': 'Unidade',
            'uev_value': 'Valor UEV',
            'source': 'Fonte',
            'category': 'Categoria',
        }