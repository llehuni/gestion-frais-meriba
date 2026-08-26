from django import forms
from django.utils import timezone
from apps.students.models import Eleve
from apps.fees.models import TypeFrais
from .models import ModePaiement


class PaiementForm(forms.Form):
    use_required_attribute = False

    eleve = forms.ModelChoiceField(
        queryset=Eleve.objects.all().select_related("classe"),
        label="Élève",
        widget=forms.HiddenInput(),
    )
    # Champ d'affichage pour la recherche HTMX (non mappé)
    eleve_search = forms.CharField(
        label="Rechercher élève",
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Tapez nom, post-nom ou matricule...", "autocomplete": "off"}),
    )
    type_frais = forms.ModelChoiceField(
        queryset=TypeFrais.objects.all(),
        label="Type de frais",
        widget=forms.Select(attrs={"class": "input"}),
    )
    montant_paye = forms.DecimalField(
        label="Montant (CDF)",
        min_value=1,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "input", "min": "1", "step": "0.01", "placeholder": "Ex: 150000"}),
    )
    date_paiement = forms.DateField(
        label="Date",
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={"class": "input", "type": "date"}, format="%Y-%m-%d"),
    )
    annee_scolaire = forms.CharField(
        label="Année scolaire",
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Ex: 2024-2025"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimiser queryset avec classe
        self.fields["eleve"].queryset = Eleve.objects.select_related("classe").order_by("nom", "prenom")
        # Si initial eleve fourni, préremplir le champ de recherche pour affichage
        initial = kwargs.get("initial", {})
        if initial.get("eleve"):
            try:
                e = initial["eleve"] if isinstance(initial["eleve"], Eleve) else Eleve.objects.get(pk=initial["eleve"])
                self.fields["eleve_search"].initial = f"{e.nom_complet} ({e.matricule} — {e.classe.nom})"
            except Exception:
                pass

    def clean_montant_paye(self):
        v = self.cleaned_data["montant_paye"]
        if v is not None and v <= 0:
            raise forms.ValidationError("Le montant doit être strictement positif.")
        return v

    def clean(self):
        cleaned = super().clean()
        # Si annee_scolaire vide, on prend celle de l'élève
        eleve = cleaned.get("eleve")
        annee = cleaned.get("annee_scolaire")
        if eleve and not annee:
            cleaned["annee_scolaire"] = eleve.annee_scolaire
        return cleaned
