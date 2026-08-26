"""
Service paiement — RG-03/04/05/07
Transaction atomique : paiement + solde/arrieres + reçu + audit
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
    """Retourne le montant dû pour ce type selon la classe de l'élève (Frais)."""
    from apps.fees.models import Frais
    frais = Frais.objects.filter(type_frais=type_frais, classes=eleve.classe).first()
    if frais:
        return frais.montant
    # fallback : frais sans classe spécifique mais même type
    frais = Frais.objects.filter(type_frais=type_frais, classes__isnull=True).first()
    if frais:
        return frais.montant
    # sinon premier frais du type
    frais = Frais.objects.filter(type_frais=type_frais).first()
    return frais.montant if frais else Decimal("0")


def get_situation_financiere(eleve, annee_scolaire=None):
    """
    Retourne détail financier pour un élève / année :
    - par type : {type, total_du, total_paye, solde, statut}
    - totaux globaux
    """
    from apps.fees.models import Frais, TypeFrais
    from apps.payments.models import Paiement

    if annee_scolaire is None:
        annee_scolaire = eleve.annee_scolaire or get_annee_scolaire_courante()

    # Tous les types qui ont un Frais lié à la classe
    frais_qs = Frais.objects.filter(classes=eleve.classe).select_related("type_frais")
    if not frais_qs.exists():
        # fallback global
        frais_qs = Frais.objects.all().select_related("type_frais")

    # Dédupliquer par type_frais (prendre montant max si doublon)
    type_map = {}
    for f in frais_qs:
        tid = f.type_frais_id
        if tid not in type_map or f.montant > type_map[tid].montant:
            type_map[tid] = f

    details = []
    total_du_global = Decimal("0")
    total_paye_global = Decimal("0")

    for frais in type_map.values():
        total_du = frais.montant
        total_paye = Paiement.objects.filter(
            eleve=eleve, type_frais=frais.type_frais, annee_scolaire=annee_scolaire
        ).aggregate(t=Sum("montant_paye"))["t"] or Decimal("0")
        solde = max(total_du - total_paye, Decimal("0"))
        if total_paye == 0:
            statut = "impaye"
        elif solde == 0:
            statut = "complet"
        else:
            statut = "partiel"
        details.append({
            "type_frais": frais.type_frais,
            "frais": frais,
            "total_du": total_du,
            "total_paye": total_paye,
            "solde": solde,
            "statut": statut,
        })
        total_du_global += total_du
        total_paye_global += total_paye

    solde_global = max(total_du_global - total_paye_global, Decimal("0"))
    arrieres = solde_global

    # Détermination statut global
    if total_paye_global == 0 and total_du_global > 0:
        statut_global = "impaye"
    elif solde_global == 0:
        statut_global = "complet"
    else:
        statut_global = "partiel"

    paiements = Paiement.objects.filter(
        eleve=eleve, annee_scolaire=annee_scolaire
    ).select_related("type_frais", "agent").order_by("-date_paiement", "-date_creation")

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
def enregistrer_paiement(*, eleve, type_frais, montant_paye, date_paiement, mode_paiement, agent, annee_scolaire=None, observation="", request=None):
    """
    Enregistre un paiement, met à jour solde/arrieres, génère reçu.
    RG-03: montant strictement positif
    RG-04: reçu numéroté auto
    RG-05: solde mis à jour en temps réel
    RG-07: journalisation
    """
    from apps.payments.models import Paiement, Recu
    from apps.audit.models import AuditLog

    if montant_paye is None or Decimal(str(montant_paye)) <= 0:
        raise ValidationError({"montant_paye": "Le montant doit être strictement positif."})

    montant_paye = Decimal(str(montant_paye))

    if annee_scolaire is None:
        annee_scolaire = eleve.annee_scolaire or get_annee_scolaire_courante()

    # Calcul total dû AVANT création
    total_du = get_total_du_for_eleve_type(eleve, type_frais)

    # Calcul total déjà payé pour ce type/année
    total_paye_avant = Paiement.objects.filter(
        eleve=eleve, type_frais=type_frais, annee_scolaire=annee_scolaire
    ).aggregate(t=Sum("montant_paye"))["t"] or Decimal("0")

    # Nouveau total payé
    nouveau_total_paye = total_paye_avant + montant_paye
    solde = max(total_du - nouveau_total_paye, Decimal("0"))

    # Calcul arrieres global avant : somme des soldes existants + solde courant si >0; on calcule via situation
    # Simplifié : arrieres = somme des soldes positifs pour élève/année après paiement
    # On doit calculer somme des soldes par type après paiement
    # Pour éviter N+1, on calcule via get_situation_financiere logique inline
    # temporairement créer paiement puis recalculer arrieres = total_du_global - total_paye_global
    # On calcule total_du_global
    from apps.fees.models import Frais
    frais_qs = Frais.objects.filter(classes=eleve.classe)
    if not frais_qs.exists():
        frais_qs = Frais.objects.all()
    type_map = {}
    for f in frais_qs.select_related("type_frais"):
        tid = f.type_frais_id
        if tid not in type_map or f.montant > type_map[tid].montant:
            type_map[tid] = f
    total_du_global = sum((f.montant for f in type_map.values()), Decimal("0"))
    total_paye_global_avant = Paiement.objects.filter(eleve=eleve, annee_scolaire=annee_scolaire).aggregate(t=Sum("montant_paye"))["t"] or Decimal("0")
    total_paye_global_apres = total_paye_global_avant + montant_paye
    arrieres = max(total_du_global - total_paye_global_apres, Decimal("0"))

    # Bonus : vérifier dépassement ? On autorise mais solde reste 0 si trop-payé (pas de remboursement auto)
    # On garde logique solde = 0 si trop-payé

    paiement = Paiement(
        eleve=eleve,
        type_frais=type_frais,
        annee_scolaire=annee_scolaire,
        montant_paye=montant_paye,
        date_paiement=date_paiement or timezone.now().date(),
        mode_paiement=mode_paiement,
        montant_total_du=total_du,
        solde=solde,
        arrieres=arrieres,
        agent=agent,
        observation=observation,
    )
    # contourner save() qui recalcule : on set puis save, mais save recalculera solde correctement en incluant exclude pk -> idem
    # On force en désactivant recalcul via override : on appelle super save via model
    # Plus simple : laisser save faire son calcul mais après on corrige arrieres
    # On va sauvegarder avec nos valeurs puis le save interne recalculera ; pour éviter double, on fait paiement.save en bypassant recalcul si on pose un flag
    # Solution : appeler directement Paiement.objects.create avec nos valeurs via super().save sans recalcul
    # Or subclass : on va sauvegarder via Paiement.save qui recalculera : testons
    # Pour garantir atomicité, on passe par save normal
    paiement.save()

    # Mettre à jour arrieres si différent du calcul save (save calcule sur base des paiements existants sans inclure global)
    # On corrige si besoin
    if paiement.arrieres != arrieres:
        Paiement.objects.filter(pk=paiement.pk).update(arrieres=arrieres)
        paiement.arrieres = arrieres

    # Créer reçu numéroté
    recu = Recu.objects.create(
        paiement=paiement,
        eleve=eleve,
        montant=montant_paye,
        agent=agent,
    )

    # Journalisation RG-07
    try:
        AuditLog.objects.create(
            user=agent,
            action="CREATE",
            model_name="Paiement",
            object_id=str(paiement.pk),
            object_repr=str(paiement),
            changes={
                "eleve": eleve.matricule,
                "type_frais": type_frais.libelle,
                "montant_paye": str(montant_paye),
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
            changes={"numero": recu.numero, "montant": str(montant_paye)},
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
        )
    except Exception:
        # Ne pas bloquer paiement si audit échoue
        pass

    return paiement, recu
