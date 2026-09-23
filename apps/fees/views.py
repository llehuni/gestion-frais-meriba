# Views fees supprimées — paramétrage retiré.
# L'admin ne paramètre plus. Redirection vers dashboard si accès ancien URL.
from django.shortcuts import redirect

# Toutes les vues précédentes (TypeFrais/Frais) sont supprimées.
# Les anciennes URLs /fees/... redirigent vers le dashboard pour éviter 500.
def deprecated_redirect(request, *args, **kwargs):
    return redirect("accounts:dashboard")
