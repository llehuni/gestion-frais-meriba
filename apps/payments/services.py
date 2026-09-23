"""
Service paiement — RG-03/04/05/07
Transaction atomique : paiement + reçu + audit
Plus de paramétrage Frais : type_frais est un attribut CharField.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone


def _get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _get_user_agent(request):
    if not request:
        return ""
    return request.META.get("HTTP_USER_AGENT", "")[:500]


def get_annee_scolaire_courante():
    from apps.students.models import get_annee_scolaire_courante as _g
    return _g()


def get_total_du_for_eleve_type(eleve, type_frais):
    """
    Historique: retournait montant dû via Frais par classe.
    Désormais sans paramétrage : retourne 0 (pas de dette prédéfinie).
    Gardé pour compatibilité d'appel — renvoie 0.
    """
    return Decimal("0")


def get_situation_financiere(eleve, annee_scolaire=None):
    """
    Retourne détail financier pour un élève / année.
    Sans table Frais : on groupe par type_frais (attribut) des Paiements existants
    et on expose aussi les types sans paiement (pour affichage complet).
    - par type : {type_frais (value), type_frais_label, total_du, total_paye, solde, statut}
    - totaux globaux: total_du = total_paye (soldé), solde=0, arrieres=0
    """
    from apps.payments.models import Paiement, TypeFrais

    if annee_scolaire is None:
        annee_scolaire = eleve.annee_scolaire or get_annee_scolaire_courante()

    details = []
    total_paye_global = Decimal("0")

    # Pour chaque choix de type, calculer total payé
    for value, label in TypeFrais.choices:
        total_paye = Paiement.objects.filter(
            eleve=eleve, type_frais=value, annee_scolaire=annee_scolaire
        ).aggregate(t=Sum("montant_paye"))["t"] or Decimal("0")
        # Sans dette prédéfinie : total_du = total_paye (soldé)
        total_du = total_paye
        solde = Decimal("0")
        if total_paye == 0:
            statut = "impaye"
        else:
            statut = "complet"
        details.append({
            "type_frais": value,
            "type_frais_label": label,
            "type_frais_display": label,
            # Compat template ancien: objet factice avec .libelle
            "type_frais_obj": type("Obj", (), {"libelle": label, "value": value})(),
            "frais": None,
            "total_du": total_du,
            "total_paye": total_paye,
            "solde": solde,
            "statut": statut,
        })
        total_paye_global += total_paye

    total_du_global = total_paye_global
    solde_global = Decimal("0")
    arrieres = Decimal("0")

    if total_paye_global == 0:
        statut_global = "impaye"
    else:
        statut_global = "complet"

    paiements = Paiement.objects.filter(
        eleve=eleve, annee_scolaire=annee_scolaire
    ).select_related("agent").order_by("-date_paiement", "-date_creation")

    return {
        "eleve": eleve,
        "annee_scolaire": annee_scolaire,
        "details": details,
        "total_du": total_du_global,
        "total_paye": total_paye_global,
        "solde": solde_global,
        "arrieres": arrieres,
        "statut": statut_global,
        "paiements": paiements,
    }


@transaction.atomic
def enregistrer_paiement(*, eleve, type_frais, montant_paye, date_paiement, mode_paiement, agent, annee_scolaire=None, observation="", devise="USD", request=None):
    """
    Enregistre un paiement, génère reçu.
    RG-03: montant strictement positif
    RG-04: reçu numéroté auto
    RG-07: journalisation
    type_frais : str value parmi TypeFrais.choices (ex: 'inscription')
    devise : USD (défaut) ou CDF
    """
    from apps.payments.models import Devise, Paiement, Recu, TypeFrais
    from apps.audit.models import AuditLog

    if montant_paye is None or Decimal(str(montant_paye)) <= 0:
        raise ValidationError({"montant_paye": "Le montant doit être strictement positif."})

    montant_paye = Decimal(str(montant_paye))

    # Validation type_frais
    valid_types = {c[0] for c in TypeFrais.choices}
    if type_frais not in valid_types:
        # accepter label casse différente ? normaliser
        # tenter mapping insensible à la casse
        lowered = str(type_frais).lower().strip()
        mapped = None
        for v, _label in TypeFrais.choices:
            if v.lower() == lowered:
                mapped = v
                break
        if mapped:
            type_frais = mapped
        else:
            raise ValidationError({"type_frais": f"Type de frais invalide: {type_frais}"})

    if annee_scolaire is None:
        annee_scolaire = eleve.annee_scolaire or get_annee_scolaire_courante()

    # Validation devise
    if devise not in dict(Devise.choices):
        devise = Devise.USD
    # Sans dette paramétrée: total_du = montant_paye, solde/arrieres =0
    total_du = montant_paye
    solde = Decimal("0")
    arrieres = Decimal("0")

    paiement = Paiement(
        eleve=eleve,
        type_frais=type_frais,
        annee_scolaire=annee_scolaire,
        montant_paye=montant_paye,
        devise=devise,
        date_paiement=date_paiement or timezone.now().date(),
        mode_paiement=mode_paiement,
        montant_total_du=total_du,
        solde=solde,
        arrieres=arrieres,
        agent=agent,
        observation=observation,
    )
    paiement.save()

    # Créer reçu numéroté
    recu = Recu.objects.create(
        paiement=paiement,
        eleve=eleve,
        montant=montant_paye,
        devise=devise,
        agent=agent,
    )

    # Journalisation RG-07 — isolée en savepoint pour ne pas rollback paiement si audit échoue
    try:
        with transaction.atomic():
            label = str(dict(TypeFrais.choices).get(type_frais, type_frais))
            AuditLog.objects.create(
                user=agent,
                action="CREATE",
                model_name="Paiement",
                object_id=str(paiement.pk),
                object_repr=str(paiement),
                changes={
                    "eleve": eleve.matricule,
                    "type_frais": label,
                    "montant_paye": str(montant_paye),
                    "devise": devise,
                    "recu": recu.numero,
                },
                ip_address=_get_client_ip(request),
                user_agent=_get_user_agent(request),
            )
            AuditLog.objects.create(
                user=agent,
                action="CREATE",
                model_name="Recu",
                object_id=str(recu.pk),
                object_repr=f"Reçu {recu.numero}",
                changes={"numero": recu.numero, "montant": str(montant_paye), "devise": devise},
                ip_address=_get_client_ip(request),
                user_agent=_get_user_agent(request),
            )
    except Exception:
        # Audit ne doit jamais bloquer le paiement ; l'exception est déjà isolée dans savepoint
        pass

    return paiement, recu
