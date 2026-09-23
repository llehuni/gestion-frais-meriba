# fees/models.py — vidé suite à la suppression du paramétrage.
# L'admin ne paramètre plus les types/montants.
# TypeFrais et Frais supprimés via migration 0003.
# type_frais est désormais un attribut CharField avec choices dans Paiement (payments.models.TypeFrais).
# On garde ce fichier vide pour compatibilité d'app, mais sans modèle.
# La table Classe reste l'unique table de paramétrage (apps.classes).
