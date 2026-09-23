"""
Seed Meriba — classes 1ère→6ème (3-4 sections), élèves 28-40/classe avec paiements.
Plus de paramétrage frais : type_frais est un attribut CharField dans Paiement (TypeFrais choices).
Usage: python manage.py seed [--clear]
Laisse les utilisateurs tel quel.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.classes.models import Classe, Niveau, Section
from apps.payments.models import TypeFrais
from apps.students.models import Eleve, Sexe, LienParente
from apps.payments.services import enregistrer_paiement


# Données réalistes congolaises
NOMS = ["Mbuyi","Kalala","Tshimanga","Ngoy","Kabongo","Mukendi","Lunda","Mwamba","Nkulu","Kaseya","Mutombo","Ilunga","Kabuya","Tshibangu","Kazadi","Mulumba","Kanku","Beya","Tshiela","Mpoyi","Sanga","Kakudji","Mbuyu","Katabana","Monga","Ngandu","Mbayo","Kalonji","Mujinga","Kasongo","Mwadi","Kabasele","Ngolo","Tshisuaka","Luboya","Kanyinda","Mbikay","Tshitenge","Kabengele","Kalamba","Mukuna","Kalombo","Kapinga","Kamitenga","Kabedi","Mbuyamba","Ntumba","Kalubi","Mbombo","Mulunda","Kashala","Tshibola","Kasai","Lukusa","Kayembe","Kabemba","Mposhi","Ngalula","Banza","Monde","Kitenge"]
POSTNOMS = ["Kalala","Ngoy","Mukendi","Mwamba","Kaseya","Ilunga","Kabuya","Kazadi","Beya","Mpoyi","Kakudji","Katabana","Mbayo","Mujinga","Kabasele","Tshisuaka","Kanyinda","Tshitenge","Kalamba","Kalombo","Kabedi","Mbombo","Tshibola","Lukusa","Ngalula","Kitenge","Mulunda","Kasai","Mbikay","Kapinga","Ntumba","Monga","Kasongo","Kanku","Mulumba","Kabongo","Lunda","Nkulu","Mutombo","Tshibangu","Banza","Mbuyi","Sanga","Mbuyu","Ngandu","Mwadi","Ngolo","Luboya","Kabengele","Mukuna","Kamitenga","Mbuyamba","Kalubi","Monde"]
PRENOMS_M = ["Jean","Paul","Alain","Pierre","Joseph","David","Michel","Bernard","Emmanuel","Daniel","Samuel","Jonathan","Isaac","Luc","Jacques","Moïse","Aaron","Josué","Salomon","Gédéon","Élie","Lionel","Patrick","Rodrigue","Joël","Junior","Glody","Héritier","Israël","Nathan","Olivier","Patient","William","Yannick","Zidane","Trésor","Dieu-Merci","Exaucé","Gloire","Grace","Merveille","Christ","Grâce","Divine","Précieux","Espérance","Béni","Trésor","Fidèle","Merdi","Lionel","Serge","Claude","Roger","André","Victor","Julien","Cédric","Fabrice","Christian","Gauthier","Héritier","Innocent","Jules","Kevin","Léon","Marc","Noël","Oscar","Pascal","Quentin","René","Sylvain","Thierry","Ulrich","Vincent","Xavier","Yves","Zacharie"]
PRENOMS_F = ["Marie","Grâce","Sarah","Christelle","Gloria","Esther","Deborah","Rachel","Naomie","Miriam","Anne","Ruth","Rebecca","Priscille","Marie-Claire","Dorcas","Sarah","Chanceline","Fideline","Merdi","Divine","Espérance","Bénie","Gracias","Merveille","Ange","Béni","Trésor","Gloire","Séraphine","Thérèse","Victoire","Christine","Elisabeth","Françoise","Hélène","Irène","Jeanne","Léontine","Marthe","Nathalie","Odette","Patience","Reine","Sylvie","Ursule","Véronique","Wivine","Yvette","Aline","Bernadette","Carine","Denise","Emilie","Florence","Gertrude","Henriette","Josiane","Clarisse","Mireille","Solange","Antoinette","Cécile","Delphine","Eugénie","Fabiola","Hortense","Immaculée","Julienne","Colette","Bijou","Excellence","Merveille","Priscilla","Quevine","Sévérine","Ursula","Viviane","Wivine","Yolande","Zaina"]

ADRESSES = ["Av. Lumumba 12, Kinshasa","Av. Kasavubu 45, Kinshasa","Q. Matonge, Kinshasa","C. Gombe, Kinshasa","Av. de l'Université, Kinshasa","Q. Bandal, Kinshasa","C. Limete, Kinshasa","Av. Kasa-Vubu, Kinshasa","Q. Ngaliema, Kinshasa","Av. Lubumbashi 8","Q. Katuba, Lubumbashi","Av. Likasi, Kolwezi","C. Commune, Kinshasa","Av. Sendwe, Kinshasa","Q. Ma Campagne, Kinshasa"]


class Command(BaseCommand):
    help = "Seed classes 1ère-6ème (A-C/D), élèves 28-40/classe avec paiements (type_frais attribut)"

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Supprime élèves/paiements existants avant seed')

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options['clear']
        random.seed(42)
        self.stdout.write(self.style.MIGRATE_HEADING("=== Seed Meriba ==="))

        # --- Agent pour paiements (laisse utilisateurs tel quel) ---
        from apps.accounts.models import User, Role
        agent = User.objects.filter(role=Role.CAISSIER, actif=True).first()
        if not agent:
            agent = User.objects.filter(role=Role.ADMINISTRATEUR, actif=True).first()
        if not agent:
            agent = User.objects.filter(is_staff=True).first()
        if not agent:
            agent = User.objects.first()
        if not agent:
            self.stdout.write(self.style.ERROR("Aucun utilisateur trouvé pour enregistrer les paiements"))
            return
        self.stdout.write(f"Agent paiements : {agent.login} ({agent.get_role_display()})")

        # --- 1. Classes 1ère-6ème 3-4 sections ---
        classes = []
        sections_map = {
            1: [Section.A, Section.B, Section.C],
            2: [Section.A, Section.B, Section.C, Section.D],
            3: [Section.A, Section.B, Section.C],
            4: [Section.A, Section.B, Section.C, Section.D],
            5: [Section.A, Section.B, Section.C],
            6: [Section.A, Section.B, Section.C, Section.D],
        }
        for niveau in range(1, 7):
            for sec in sections_map[niveau]:
                c, created = Classe.objects.get_or_create(niveau=niveau, section=sec)
                classes.append(c)
                if created:
                    self.stdout.write(f"  Classe créée {c.nom}")
        self.stdout.write(self.style.SUCCESS(f"Classes : {len(classes)} (21)"))

        # --- 2. Types de frais désormais attributs (pas de table) ---
        # Montants indicatifs pour génération de paiements aléatoires
        types_data = [
            (TypeFrais.SCOLARITE, Decimal("360")),
            (TypeFrais.INSCRIPTION, Decimal("30")),
            (TypeFrais.AUTRES, Decimal("20")),
        ]
        self.stdout.write(self.style.SUCCESS(f"Types (attributs) : {len(types_data)} — {[v for v,_ in types_data]}"))

        # --- 3. Élèves ---
        if clear:
            from apps.payments.models import Paiement, Recu
            self.stdout.write("Clear élèves/paiements/reçus...")
            Recu.objects.all().delete()
            Paiement.objects.all().delete()
            Eleve.objects.all().delete()
        existing = Eleve.objects.count()
        if existing and not clear:
            self.stdout.write(self.style.WARNING(f"{existing} élèves existants — ajout seulement si besoin (utilise --clear pour reset)"))

        total_created = 0
        for classe in sorted(classes, key=lambda c: (c.niveau, c.section)):
            current = classe.eleves.count()
            target = random.randint(28, 40)
            to_create = max(0, target - current) if not clear else target
            if to_create == 0:
                continue
            self.stdout.write(f"  {classe.nom}: {current} existants, création {to_create} (cible {target})")
            for _ in range(to_create):
                sexe = random.choice([Sexe.M, Sexe.F])
                prenom = random.choice(PRENOMS_M if sexe == Sexe.M else PRENOMS_F)
                nom = random.choice(NOMS)
                post_nom = random.choice(POSTNOMS)
                start = date(2014, 1, 1)
                end = date(2020, 12, 31)
                delta = (end - start).days
                dob = start + timedelta(days=random.randint(0, delta))
                adresse = random.choice(ADRESSES)
                lien = random.choice(list(LienParente.values))
                tel = f"+243 81{random.randint(1000000, 9999999)}"
                tuteur_nom = f"{random.choice(NOMS)} {random.choice(POSTNOMS)}"
                eleve = Eleve(
                    nom=nom, post_nom=post_nom, prenom=prenom, sexe=sexe,
                    date_naissance=dob, adresse=adresse, classe=classe,
                    tuteur_nom=tuteur_nom, tuteur_lien=lien, tuteur_telephone=tel
                )
                eleve.save()
                total_created += 1
        self.stdout.write(self.style.SUCCESS(f"Élèves créés : {total_created} (total {Eleve.objects.count()})"))

        # --- 4. Situations (paiements) ---
        eleves = list(Eleve.objects.select_related("classe").all())
        from apps.payments.models import Paiement
        created_paiements = 0
        for eleve in eleves:
            if not clear and Paiement.objects.filter(eleve=eleve).exists():
                continue
            r = random.random()
            if r < 0.55:
                profil = "complet"
            elif r < 0.80:
                profil = "partiel"
            else:
                profil = "impaye"
            for type_val, montant in types_data:
                if profil == "complet":
                    paye = montant
                elif profil == "partiel":
                    if random.random() < 0.7:
                        paye = montant
                    else:
                        pct = random.uniform(0.4, 0.8)
                        paye = (montant * Decimal(str(round(pct, 2)))).quantize(Decimal("0.01"))
                        if paye < 5:
                            paye = (montant / 2).quantize(Decimal("0.01"))
                else:
                    if random.random() < 0.55:
                        continue
                    else:
                        pct = random.uniform(0.1, 0.5)
                        paye = (montant * Decimal(str(round(pct, 2)))).quantize(Decimal("0.01"))
                start_pay = date(2025, 9, 15)
                end_pay = date(2026, 6, 15)
                delta_pay = (end_pay - start_pay).days
                dpay = start_pay + timedelta(days=random.randint(0, delta_pay))
                try:
                    enregistrer_paiement(
                        eleve=eleve, type_frais=type_val, montant_paye=paye,
                        date_paiement=dpay, mode_paiement="especes",
                        agent=agent, annee_scolaire=eleve.annee_scolaire,
                        observation="", request=None
                    )
                    created_paiements += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f" Paiement échoué {eleve.matricule} {type_val}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Paiements créés : {created_paiements}"))

        # Résumé situations
        from apps.payments.services import get_situation_financiere
        a_jour = impaye = 0
        for e in Eleve.objects.all():
            sit = get_situation_financiere(e)
            if sit["total_paye"] > 0:
                a_jour += 1
            else:
                impaye += 1
        self.stdout.write(self.style.MIGRATE_HEADING(f"Situations — À jour (payé>0): {a_jour} | Sans paiement: {impaye} | Total élèves: {Eleve.objects.count()} | Total classes: {Classe.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("Seed terminé."))
