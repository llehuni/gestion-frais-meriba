# Migration suppression paramétrage : on garde seulement Classe, type_frais devient attribut Paiement
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0002_frais_devise"),
        ("payments", "0002_type_frais_to_charfield"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="frais",
            name="classes",
        ),
        migrations.RemoveField(
            model_name="frais",
            name="type_frais",
        ),
        migrations.DeleteModel(
            name="Frais",
        ),
        migrations.DeleteModel(
            name="TypeFrais",
        ),
    ]
