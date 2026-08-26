from django import forms
from .models import Classe


class ClasseForm(forms.ModelForm):
    use_required_attribute = False
    class Meta:
        model = Classe
        fields = ["niveau", "section"]
        widgets = {
            "niveau": forms.Select(attrs={"class": "input"}),
            "section": forms.Select(attrs={"class": "input"}),
        }
