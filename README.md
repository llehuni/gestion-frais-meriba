# Gestion des frais scolaires — Complexe Scolaire Meriba

Application web de gestion des frais scolaires du Complexe Scolaire Meriba, destinée au cycle primaire (1ʳᵉ à 6ᵉ).
Elle centralise la gestion des élèves, des classes, des frais, des paiements, des reçus et des rapports financiers pour le secrétariat, la caisse et la direction.

## Guide d'installation

### 1. Prérequis

- Python 3.10 ou supérieur (`python --version`)
- Git
- MySQL 8 pour un usage en production, mais le projet prend automatiquement le mode SQLite en fallback si MySQL n'est pas disponible ou si `mysqlclient` n'est pas installé

### 2. Récupérer le projet

```bash
git clone <url-du-depot>
cd gestion-frais-meriba
```

### 3. Créer l'environnement virtuel et installer les dépendances

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copiez le fichier d'exemple puis renseignez les valeurs adaptées à votre environnement :

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Le projet charge automatiquement les variables depuis `.env` via `python-dotenv`.

#### Option A — MySQL

```ini
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DB_ENGINE=django.db.backends.mysql
DB_NAME=gestion_frais_meriba
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Créer la base avant migration :

```sql
CREATE DATABASE gestion_frais_meriba CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### Option B — SQLite (pratique pour le développement)

```ini
DB_ENGINE=django.db.backends.sqlite3
DB_NAME_SQLITE=db.sqlite3
```

Si MySQL est demandé mais que `mysqlclient` n'est pas installé, l'application bascule automatiquement sur SQLite pour continuer à fonctionner en développement.

### 5. Appliquer les migrations

```bash
python manage.py migrate
```

### 6. Charger les données de démonstration (facultatif)

```bash
python manage.py loaddata fixtures/seed_meriba.json
```

#### Comptes de démonstration inclus dans le seed

| Rôle | Login | Mot de passe |
| --- | --- | --- |
| Administrateur | `aphia` | `Aphia123!` |
| Secrétaire | `secretaire` | `Secretaire123!` |
| Caissier | `caissier` | `Caissier123!` |
| Direction | `direction` | `Direction123!` |

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Puis ouvrez :

```text
http://127.0.0.1:8000
```

### 8. Vérifications

```bash
python manage.py check
python manage.py test
```

## Licence

Interne — Complexe Scolaire Meriba.
