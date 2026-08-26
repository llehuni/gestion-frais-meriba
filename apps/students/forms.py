from django import forms
from .models import Eleve


class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            "nom", "post_nom", "prenom", "sexe", "date_naissance", "adresse",
            "classe",
            "tuteur_nom", "tuteur_lien", "tuteur_telephone",
        ]
        widgets = {
            "nom": forms.TextInput(attrs={"class": "input"}),
            "post_nom": forms.TextInput(attrs={"class": "input"}),
            "prenom": forms.TextInput(attrs={"class": "input"}),
            "sexe": forms.Select(attrs={"class": "input"}),
            "date_naissance": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "adresse": forms.TextInput(attrs={"class": "input"}),
            "classe": forms.Select(attrs={"class": "input"}),
            "tuteur_nom": forms.TextInput(attrs={"class": "input"}),
            "tuteur_lien": forms.Select(attrs={"class": "input"}),
            "tuteur_telephone": forms.TextInput(attrs={"class": "input", "placeholder": "+243 ..."}),
        }
