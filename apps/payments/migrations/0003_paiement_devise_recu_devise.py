# Migration ajout devise USD par défaut pour Paiement et Recu
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_type_frais_to_charfield"),
    ]

    operations = [
        migrations.AddField(
            model_name="paiement",
            name="devise",
            field=models.CharField(choices=[("USD", "USD"), ("CDF", "CDF")], db_index=True, default="USD", max_length=3, verbose_name="devise"),
        ),
        migrations.AddField(
            model_name="recu",
            name="devise",
            field=models.CharField(choices=[("USD", "USD"), ("CDF", "CDF")], default="USD", max_length=3, verbose_name="devise"),
        ),
    ]
