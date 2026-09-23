# Migration: type_frais devient CharField (suppression paramétrage frais)
# 1) ajoute champ temporaire CharField
# 2) copie les libellés existants via mapping vers choices
# 3) supprime ancien FK et renomme
import unicodedata
from django.db import migrations, models


def _norm(s: str) -> str:
    # normalise sans accent, lower
    if not s:
        return ""
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.strip()


def map_libelle_to_choice(libelle: str) -> str:
    n = _norm(libelle)
    if "inscription" in n:
        return "inscription"
    if "scol" in n:
        return "scolarite"
    if "examen" in n:
        return "examens"
    if "bulletin" in n:
        return "bulletin"
    if "autre" in n or "divers" in n or "suivi" in n or "encadrement" in n:
        return "autres"
    # fallback selon libelle exact original
    if n in ("inscription", "scolarite", "examens", "bulletin", "autres"):
        return n
    return "autres"


def copy_type_frais(apps, schema_editor):
    Paiement = apps.get_model("payments", "Paiement")
    TypeFrais = apps.get_model("fees", "TypeFrais")
    # map id -> choice
    id_to_choice = {}
    for tf in TypeFrais.objects.all():
        id_to_choice[tf.id] = map_libelle_to_choice(tf.libelle)
    for p in Paiement.objects.all().iterator():
        # old FK still available as type_frais_id in DB, but after AddField we have new column
        # Access via raw? Use getattr for type_frais_id
        old_id = getattr(p, "type_frais_id", None)
        choice = id_to_choice.get(old_id, "autres")
        # type_frais_tmp is new char field
        p.type_frais_tmp = choice
        p.save(update_fields=["type_frais_tmp"])


def reverse_copy(apps, schema_editor):
    # reverse: try to map back to FK - best effort, create type if needed
    Paiement = apps.get_model("payments", "Paiement")
    TypeFrais = apps.get_model("fees", "TypeFrais")
    # ensure Types exist
    libelle_map = {
        "inscription": "Inscription",
        "scolarite": "Scolarité",
        "examens": "Examens",
        "bulletin": "Bulletin",
        "autres": "Autres contributions",
    }
    for choice, libelle in libelle_map.items():
        TypeFrais.objects.get_or_create(libelle=libelle, defaults={"description": ""})
    choice_to_id = {map_libelle_to_choice(tf.libelle): tf.id for tf in TypeFrais.objects.all()}
    for p in Paiement.objects.all().iterator():
        choice = getattr(p, "type_frais", None)
        if choice in choice_to_id:
            p.type_frais_id = choice_to_id[choice]
            p.save(update_fields=["type_frais"])


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0002_frais_devise"),
        ("payments", "0001_initial"),
    ]

    operations = [
        # 1. Ajouter champ temporaire CharField
        migrations.AddField(
            model_name="paiement",
            name="type_frais_tmp",
            field=models.CharField(
                choices=[
                    ("inscription", "Inscription"),
                    ("scolarite", "Scolarité"),
                    ("examens", "Examens"),
                    ("bulletin", "Bulletin"),
                    ("autres", "Autres contributions"),
                ],
                default="scolarite",
                max_length=30,
                verbose_name="type de frais",
                db_index=True,
                null=True,
                blank=True,
            ),
        ),
        # 2. Copier données
        migrations.RunPython(copy_type_frais, reverse_copy),
        # 3. Supprimer ancien FK
        migrations.RemoveField(
            model_name="paiement",
            name="type_frais",
        ),
        # 4. Renommer tmp -> type_frais
        migrations.RenameField(
            model_name="paiement",
            old_name="type_frais_tmp",
            new_name="type_frais",
        ),
        # 5. Rendre non-null et final
        migrations.AlterField(
            model_name="paiement",
            name="type_frais",
            field=models.CharField(
                choices=[
                    ("inscription", "Inscription"),
                    ("scolarite", "Scolarité"),
                    ("examens", "Examens"),
                    ("bulletin", "Bulletin"),
                    ("autres", "Autres contributions"),
                ],
                default="scolarite",
                max_length=30,
                verbose_name="type de frais",
                db_index=True,
            ),
        ),
    ]
