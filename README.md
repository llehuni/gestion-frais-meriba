# Gestion des frais scolaires — Complexe Scolaire Meriba

Système informatisé de gestion des frais scolaires du cycle primaire (1ʳᵉ à 6ᵉ). Projet Django monolithique.

> Source de vérité : `AGENT.md` + `BASE_CONNAISSANCE_IA_MERIBA_V2.md`. Aucune fonctionnalité hors périmètre sans validation.

## Stack (AGENT.md §5)

- **Backend** : Python 3.14 + Django 6.1 (MVT monolithique)
- **Templates** : Jinja2 (moteur principal) + DTL admin
- **CSS** : Bulma CSS
- **Interactions** : HTMX
- **DB** : MySQL en production, SQLite en développement
- **VCS** : Git

## Architecture

Client-Serveur 3 couches : Présentation (Bulma + HTMX) / Applicative-Métier (Django ORM + services) / Données (MySQL).

## Structure

```
.
├── config/           # configuration Django (settings, urls, wsgi, asgi)
├── apps/             # apps métier (accounts, students, classes, fees, payments, reports, audit)
├── templates/        # templates globaux
├── static/           # assets statiques
├── media/            # uploads (ignoré par git, .gitkeep présent)
├── docs/             # documentation
├── requirements/     # dépendances (base.txt, dev.txt)
├── manage.py
├── .env.example
├── AGENT.md
└── BASE_CONNAISSANCE_IA_MERIBA_V2.md
```

Squelette initial uniquement : aucune logique métier implémentée.

## Installation (dev)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # renseigner SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Vérifications :

```bash
python manage.py check
python manage.py test
```

## Rôles (AGENT.md §4)

Administrateur, Secrétaire, Caissier, Direction, Tuteur (externe non connecté).

## Règles métier critiques

RG-01 matricule unique, RG-03 paiement >0, RG-04 reçu numéroté, RG-05 solde temps réel, RG-06 droits par rôle, RG-07 traçabilité, RG-08 suppression protégée.

## Sécurité

Auth par Django, permissions serveur, CSRF, validation serveur, mots de passe hachés, pas de secrets en git, HTTPS en prod.

## Licence

Interne - Complexe Scolaire Meriba.
