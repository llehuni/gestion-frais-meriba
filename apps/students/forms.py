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
            "nom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Mbuyi"}),
            "post_nom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Kalala"}),
            "prenom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Jean"}),
            "sexe": forms.Select(attrs={"class": "input"}),
            "date_naissance": forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
            "adresse": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Av. Lumumba 12, Kinshasa"}),
            "classe": forms.Select(attrs={"class": "input"}),
            "tuteur_nom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Kalala Pierre"}),
            "tuteur_lien": forms.Select(attrs={"class": "input"}),
            "tuteur_telephone": forms.TextInput(attrs={"class": "input", "placeholder": "+243 900 000 000"}),
        }
