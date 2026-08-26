from django import forms
from .models import Frais, TypeFrais
from apps.classes.models import Classe


class TypeFraisForm(forms.ModelForm):
    use_required_attribute = False
    class Meta:
        model = TypeFrais
        fields = ["libelle", "description"]
        widgets = {
            "libelle": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Inscription"}),
            "description": forms.Textarea(attrs={"class": "input", "rows": 3, "placeholder": "Ex: Frais d'inscription annuelle obligatoire"}),
        }


class FraisForm(forms.ModelForm):
    use_required_attribute = False
    classes = forms.ModelMultipleChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Classes concernées"
    )

    class Meta:
        model = Frais
        fields = ["type_frais", "montant", "classes"]
        widgets = {
            "type_frais": forms.Select(attrs={"class": "input"}),
            "montant": forms.NumberInput(attrs={"class": "input", "min": "1", "step": "0.01", "placeholder": "Ex: 75000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si édition, pré-remplir classes
        if self.instance and self.instance.pk:
            self.fields["classes"].initial = self.instance.classes.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
            # Gérer M2M manuellement car on a surchargé
            instance.classes.set(self.cleaned_data["classes"])
        return instance
