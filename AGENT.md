# AGENT.md — Gestion des frais scolaires du Complexe Scolaire Meriba

## 1. Mission

Tu es un agent de développement logiciel intervenant sur le projet :

**Système informatisé de gestion des frais scolaires du Complexe Scolaire Meriba (cycle primaire).**

Ta mission est de contribuer au développement d’une application web fiable, sécurisée, maintenable et adaptée au fonctionnement réel du secrétariat, de la caisse et de la direction de l’établissement.

Le produit doit rester strictement aligné sur la base de connaissance, le cahier des charges, les besoins fonctionnels et les modèles UML fournis dans le dépôt.

> **Principe directeur : le code doit implémenter le projet, pas inventer un nouveau projet.**

---

## 2. Source de vérité

Avant toute implémentation ou modification importante :

1. Lire la **BASE_CONNAISSANCE_IA_MERIBA_V2.md** (ou tout fichier de spécification équivalent).
2. Vérifier les besoins fonctionnels et les user stories concernés.
3. Vérifier les contraintes techniques et les rôles des utilisateurs.
4. Vérifier les modèles UML lorsqu’ils concernent la fonctionnalité.
5. Vérifier le code existant avant de créer une nouvelle abstraction.

En cas de contradiction entre une demande ponctuelle et une spécification existante :
- identifier explicitement la contradiction ;
- ne pas inventer une règle métier ;
- privilégier la spécification validée du projet ;
- signaler la contradiction avant une modification structurante.

Ne jamais considérer une hypothèse comme une exigence.

---

## 3. Périmètre fonctionnel

Le système couvre principalement :

- authentification et gestion des utilisateurs ;
- gestion des rôles et permissions ;
- enregistrement des élèves (matricule, identité, classe, tuteur) ;
- paramétrage des classes (1ʳᵉ à 6ᵉ primaire) ;
- paramétrage des années scolaires ;
- paramétrage des types de frais (inscription, scolarité, examens, bulletin, autres) ;
- définition des montants de frais par classe ;
- enregistrement des paiements ;
- édition automatique des reçus numérotés ;
- mise à jour en temps réel du solde et des arriérés ;
- consultation des situations financières (détail, total dû, solde, arriérés) ;
- production de rapports (recettes, débiteurs, statistiques par classe) ;
- export PDF/Excel des rapports ;
- journalisation des opérations sensibles.

### Hors périmètre

Ne pas implémenter sans validation explicite :

- autres cycles que le primaire ;
- gestion pédagogique (notes, bulletins scolaires, etc.) ;
- gestion des ressources humaines ;
- comptabilité complète (grand livre, bilan, etc.) ;
- gestion de bibliothèque ;
- gestion d’internat ;
- paiements électroniques ou bancaires ;
- fonctionnalités métier non prévues dans le cahier des charges.

Toute fonctionnalité supplémentaire doit être considérée comme une extension de périmètre, pas comme une amélioration anodine.

---

## 4. Acteurs et responsabilités métier

Les principaux acteurs sont :

### Administrateur du système
- gérer les comptes utilisateurs ;
- attribuer les rôles ;
- activer/désactiver les comptes ;
- paramétrer les types de frais ;
- paramétrer les années scolaires ;
- définir les montants des frais par classe ;
- assurer la maintenance, les sauvegardes et la consultation des journaux d’audit.

### Secrétaire administratif
- enregistrer, modifier et consulter les élèves ;
- gérer les classes et les années scolaires ;
- s’assurer de l’unicité du matricule.

### Chargé des finances / Caissier
- rechercher un élève ;
- enregistrer les paiements ;
- éditer les reçus numérotés ;
- consulter les situations financières (soldes, arriérés) ;
- suivre les impayés.

### Direction
- consulter les rapports financiers ;
- consulter les tableaux de bord et indicateurs ;
- suivre les tendances des impayés ;
- valider les paramètres généraux.

### Tuteur (acteur externe)
- acteur externe non connecté au système ;
- destinataire des reçus et des informations financières.

---

## 5. Stack technique imposée par le projet

### Backend
- Python 3
- Django
- architecture monolithique Django/MVT

### Frontend
- Jinja2 (moteur de templates)
- Bulma CSS (framework CSS responsive)
- HTMX pour les interactions dynamiques sans rechargement complet lorsque pertinent

### Base de données
- MySQL

### Outils
- Git (contrôle de version)
- (Environnement de développement à définir, mais VS Code ou équivalent recommandé)

Ne pas remplacer ces technologies par React, Vue, Angular, Node.js, MongoDB ou une architecture microservices sans décision explicite du responsable du projet.

---

## 6. Architecture

Le projet utilise une **architecture client-serveur à trois couches logicielles**.

### Couche Présentation
- Interface entre les acteurs et l'application
- Tableaux de bord, formulaires, reçus, saisies utilisateur
- HTML + Bulma CSS + HTMX

### Couche Applicative / Métier
- Cœur du système
- Requêtes, règles métier, authentification
- Échanges avec la base via l’ORM Django

### Couche Données / Persistance
- Stockage, récupération et intégrité des données financières et administratives
- MySQL

### Architecture physique
- **Serveur** : application Django + base MySQL, en local ou dans le Cloud.
- **Postes clients** : secrétariat, caisse, direction.
- **Réseau** : LAN stable ; HTTPS/SSL/TLS pour protéger les communications.

---

## 7. Structure Django recommandée

Adapter cette structure à l’état réel du dépôt plutôt que de réorganiser arbitrairement un projet existant.

```text
project/
├── manage.py
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/          # gestion des utilisateurs
│   ├── students/          # élèves
│   ├── classes/           # classes et années scolaires
│   ├── fees/              # types de frais et montants
│   ├── payments/          # paiements, reçus, soldes
│   ├── reports/           # rapports et statistiques
│   └── audit/             # journalisation et traçabilité
│
├── templates/
├── static/
├── media/
├── tests/
├── requirements/
├── docs/
├── .env.example
├── .gitignore
├── README.md
└── AGENT.md
```

Cette structure est une recommandation de séparation fonctionnelle. Elle ne doit pas être appliquée mécaniquement si le dépôt possède déjà une structure cohérente.

---

## 8. Règles métier critiques

### RG-01 — Unicité du matricule
Chaque élève possède un matricule unique. Le système doit refuser tout doublon.

### RG-02 — Champs obligatoires
Les champs obligatoires (nom, prénom, classe, etc.) doivent être renseignés avant validation.

### RG-03 — Paiement strictement positif
Un paiement nul ou négatif est refusé.

### RG-04 — Reçu numéroté
Chaque reçu possède un numéro unique, généré automatiquement.

### RG-05 — Mise à jour en temps réel
Le solde et les arriérés doivent être mis à jour immédiatement après chaque paiement.

### RG-06 — Droits dépendants du rôle
Les accès et les actions possibles dépendent strictement du rôle de l’utilisateur.

### RG-07 — Traçabilité
Toute opération sensible (création, modification, suppression, paiement) doit être journalisée avec l’identifiant de l’agent, la date et l’heure.

### RG-08 — Suppression protégée
Une classe ou un type de frais déjà associé à des opérations (élèves, paiements) ne peut pas être supprimé.

### RG-09 — Audit des connexions
Les connexions et les actions des utilisateurs doivent être enregistrées pour permettre un audit ultérieur.

---

## 9. Sécurité et confidentialité

Le système manipule des données financières et personnelles sensibles (élèves, tuteurs, montants).

La sécurité n’est donc pas une fonctionnalité « à faire plus tard ».

### Obligations

- authentification sécurisée ;
- autorisation basée sur les rôles ;
- permissions vérifiées côté serveur ;
- mots de passe gérés par les mécanismes sécurisés de Django ;
- protection CSRF ;
- validation des entrées utilisateur ;
- protection contre les injections SQL et XSS ;
- sessions sécurisées ;
- HTTPS/TLS en déploiement en ligne ;
- journalisation des actions sensibles ;
- sauvegardes automatiques et régulières ;
- absence de données sensibles dans les logs inutiles.

### Interdictions

Ne jamais :

- stocker un mot de passe en clair ;
- mettre des secrets dans Git ;
- contourner les permissions côté backend ;
- faire confiance uniquement aux contrôles de l’interface ;
- exposer inutilement des données financières ou personnelles dans une réponse HTTP ;
- désactiver une protection Django pour « faire fonctionner » une fonctionnalité.

---

## 10. Autorisations

Toute opération sensible doit être contrôlée côté serveur.

Exemple conceptuel :

```text
Administrateur
 ├── gérer utilisateurs
 ├── gérer rôles
 ├── gérer types de frais
 ├── gérer montants par classe
 ├── gérer années scolaires
 └── consulter journaux d’audit

Secrétaire
 ├── enregistrer élève
 ├── modifier élève
 ├── consulter élève
 ├── gérer classes
 └── gérer années scolaires

Caissier
 ├── rechercher élève
 ├── enregistrer paiement
 ├── éditer reçu
 ├── consulter solde
 └── consulter arriérés

Direction
 ├── consulter rapports
 ├── consulter tableaux de bord
 └── suivre impayés
```

Ne jamais utiliser uniquement une condition dans le template comme mécanisme d’autorisation.

---

## 11. Modélisation et cohérence UML

Le développement doit rester cohérent avec les modèles UML du projet :

- diagrammes de cas d’utilisation (global + sous‑ensembles) ;
- diagramme de classes (hiérarchie Utilisateur, Eleve, Classe, Frais, Paiement, etc.) ;
- diagrammes de séquence (si disponibles) ;
- diagramme de composants (si disponible).

Lorsqu’une modification implique le modèle métier :

1. identifier les classes concernées ;
2. vérifier leurs relations ;
3. vérifier les multiplicités (cardinalités) ;
4. vérifier les responsabilités ;
5. vérifier les interactions ;
6. mettre à jour la documentation UML si nécessaire.

Ne pas créer de modèle de données uniquement parce qu’un écran en a besoin.

Le modèle métier doit guider l’interface, et non l’inverse.

---

## 12. Modèles Django

### Principes

- Utiliser des relations Django explicites.
- Choisir soigneusement `ForeignKey`, `OneToOneField` et `ManyToManyField`.
- Définir les contraintes d’intégrité au niveau du modèle lorsque pertinent.
- Ajouter des index sur les champs réellement utilisés pour la recherche (matricule, nom, classe).
- Utiliser des choix (`choices`) lorsque le domaine impose un ensemble fermé de valeurs (ex. : modes de paiement, types de frais).
- Éviter les champs génériques ou JSON pour remplacer une modélisation relationnelle claire.
- Ne pas dupliquer inutilement les données.

### Données historiques

Les informations financières importantes (paiements, soldes) doivent conserver leur historique. Les suppressions physiques sont interdites lorsqu’elles détruiraient une information nécessaire à la traçabilité (préférer un champ `actif` ou `archivé`).

---

## 13. Views, Forms et Services

### Views

Une view doit principalement :

1. recevoir la requête ;
2. vérifier les permissions ;
3. récupérer ou valider les données ;
4. appeler la logique métier appropriée ;
5. retourner une réponse.

Éviter les views de plusieurs centaines de lignes.

### Forms

Utiliser les Django Forms / ModelForms pour :

- validation ;
- nettoyage des données ;
- messages d’erreur ;
- cohérence des champs.

La validation métier critique (ex. : unicité du matricule, paiement positif) doit rester côté serveur.

### Services

Utiliser une couche de service lorsque :

- une opération implique plusieurs modèles (ex. : paiement + mise à jour solde + génération reçu) ;
- une transaction métier est complexe ;
- une logique doit être réutilisée ;
- la logique ne devrait pas vivre dans une view ou un template.

---

## 14. Transactions

Pour les opérations métier impliquant plusieurs écritures liées (ex. : enregistrement d’un paiement avec mise à jour du solde et création du reçu) :

```python
from django.db import transaction

with transaction.atomic():
    # enregistrement du paiement
    # mise à jour du solde
    # génération du reçu
    ...
```

Utiliser les transactions lorsque l’intégrité de l’opération l’exige.

Un paiement ne doit pas se retrouver à moitié enregistré parce qu'une étape secondaire a échoué.

---

## 15. Templates et interface

L’interface doit être :

- simple ;
- claire ;
- professionnelle ;
- responsive ;
- adaptée au personnel administratif et financier ;
- cohérente avec les rôles ;
- orientée vers l’efficacité opérationnelle.

### Bulma CSS

- privilégier les classes utilitaires cohérentes ;
- éviter les styles inline inutiles ;
- factoriser les composants récurrents ;
- maintenir une hiérarchie visuelle claire.

### HTMX

Utiliser HTMX lorsqu'il permet de simplifier une interaction serveur sans introduire une SPA inutile.

Exemples pertinents :

- recherche d’élève ;
- filtrage de listes ;
- affichage de la situation financière ;
- mise à jour partielle d’un tableau de paiements ;
- soumission de formulaire avec retour partiel.

Ne pas utiliser HTMX partout par principe.

---

## 16. Recherche et consultation

La recherche d’élève est une fonctionnalité critique.

Elle doit :

- être rapide ;
- respecter les permissions ;
- utiliser des champs indexés (matricule, nom, classe) ;
- éviter les requêtes N+1 ;
- ne pas exposer de résultats à un utilisateur non autorisé.

Avant d'ajouter une recherche complexe :

1. identifier les champs recherchables ;
2. vérifier les besoins du cahier des charges ;
3. vérifier les performances ;
4. ajouter les index nécessaires si justifié.

---

## 17. Performance

Toujours surveiller les problèmes classiques Django :

- N+1 queries ;
- requêtes inutiles ;
- chargement excessif de relations ;
- absence d’index ;
- pagination manquante sur les listes volumineuses ;
- calculs lourds dans les templates.

Utiliser notamment lorsque pertinent :

```python
select_related()
prefetch_related()
```

Ne pas optimiser prématurément. Mesurer ou identifier un besoin réel avant d'ajouter de la complexité.

---

## 18. Rapports et statistiques

Les rapports doivent être produits à partir des données réellement enregistrées dans le système.

Ils doivent notamment couvrir :

- recettes journalières, hebdomadaires, mensuelles, annuelles ;
- liste des élèves à jour ;
- liste des débiteurs (arriérés) ;
- recettes par type de frais ;
- statistiques par classe.

Les rapports détaillés doivent être accessibles uniquement aux utilisateurs habilités (Direction, Administrateur).

Les exports prévus sont :

- PDF ;
- Excel.

Ne pas créer de données fictives pour remplir une interface de démonstration une fois le système connecté aux données réelles.

---

## 19. Tests

Chaque fonctionnalité importante doit être testée.

Priorité aux tests :

1. permissions et sécurité ;
2. règles métier (unicité, calculs de solde, etc.) ;
3. modèles et contraintes ;
4. formulaires et validations ;
5. views ;
6. intégrations entre modules ;
7. rendu/interface lorsque pertinent.

Exécuter les tests avant de considérer une fonctionnalité comme terminée.

Commande de référence :

```bash
python manage.py test
```

Si le dépôt utilise une autre commande de test, suivre la commande réellement configurée dans le projet.

---

## 20. Qualité du code

Principes prioritaires :

- KISS ;
- DRY ;
- SOLID lorsque pertinent ;
- séparation des responsabilités ;
- faible couplage ;
- forte cohésion ;
- lisibilité avant sophistication.

### Python

- respecter PEP 8 ;
- utiliser des noms explicites ;
- privilégier les fonctions courtes ;
- éviter les abstractions prématurées ;
- utiliser les type hints lorsqu’ils apportent une vraie valeur.

### Django

- respecter les conventions Django ;
- exploiter les mécanismes natifs avant d'ajouter une dépendance ;
- ne pas réimplémenter l’authentification ou les protections de sécurité existantes.

### Nommage

Le code utilise des noms techniques en anglais.

Exemples :

```text
Student
Class
SchoolYear
FeeType
Fee
Payment
Receipt
User
```

Les libellés affichés à l'utilisateur peuvent être en français.

---

## 21. Dépendances

Avant d'ajouter une bibliothèque :

1. vérifier si Django ou une dépendance existante fournit déjà la fonctionnalité ;
2. vérifier si la bibliothèque est réellement nécessaire ;
3. vérifier sa maintenance et sa compatibilité ;
4. limiter les dépendances au strict nécessaire.

Ne pas ajouter une bibliothèque simplement parce qu’elle rend une tâche légèrement plus confortable.

Chaque dépendance est une petite dette technique qui vient réclamer son loyer plus tard.

---

## 22. Git

Utiliser Git pour conserver un historique propre.

### Commits

Les commits doivent :

- être atomiques ;
- décrire clairement l’intention ;
- éviter de mélanger plusieurs fonctionnalités ;
- ne pas contenir de secrets.

Exemples :

```text
feat: add student enrollment form
feat: implement payment recording with receipt generation
fix: enforce unique matricule validation
test: add fee calculation tests
refactor: extract payment service
docs: update setup instructions
```

Ne jamais committer :

- `.env` ;
- mots de passe ;
- clés API ;
- certificats privés ;
- données réelles d’élèves ou de paiements ;
- dumps de base contenant des données sensibles.

---

## 23. Workflow obligatoire de développement

Pour toute tâche non triviale :

### Étape 1 — Comprendre

Lire :

- la demande ;
- les fichiers concernés ;
- le code existant ;
- les modèles ;
- les tests ;
- la documentation pertinente.

### Étape 2 — Planifier

Identifier :

- les fichiers à modifier ;
- les nouveaux fichiers nécessaires ;
- les dépendances ;
- les risques ;
- les tests à ajouter.

### Étape 3 — Implémenter

Modifier uniquement ce qui est nécessaire.

Ne pas effectuer de refactorisation opportuniste sans rapport avec la tâche.

### Étape 4 — Vérifier

Lancer :

- les tests ;
- les vérifications Django ;
- les outils de lint/formatage disponibles ;
- les vérifications pertinentes à la fonctionnalité.

Exemples :

```bash
python manage.py check
python manage.py test
```

### Étape 5 — Relire

Avant de terminer :

- vérifier les permissions ;
- vérifier les erreurs ;
- vérifier les migrations ;
- vérifier les régressions ;
- vérifier les données exposées ;
- vérifier la cohérence avec le cahier des charges.

### Étape 6 — Résumer

Présenter clairement :

- ce qui a été modifié ;
- les tests exécutés ;
- les éventuels problèmes restants ;
- les décisions nécessitant validation.

---

## 24. Migrations

Toute modification de modèle doit être accompagnée de migrations appropriées.

Utiliser :

```bash
python manage.py makemigrations
python manage.py migrate
```

Ne jamais modifier manuellement une migration déjà appliquée en production sans raison extrêmement claire.

Avant une migration :

- comprendre son impact ;
- vérifier les données existantes ;
- éviter les opérations destructives non nécessaires.

---

## 25. Gestion des erreurs

Les erreurs doivent être :

- explicites ;
- compréhensibles ;
- traçables ;
- sûres.

Ne jamais exposer :

- stack traces ;
- secrets ;
- détails internes ;
- données financières ou personnelles inutiles.

Ne pas utiliser :

```python
except Exception:
    pass
```

pour masquer un problème.

Une erreur silencieuse n'est pas une fonctionnalité. C'est juste un problème qui a appris à se cacher.

---

## 26. Données de développement

Utiliser uniquement des données fictives pour le développement et les tests.

Ne jamais intégrer dans le dépôt :

- noms réels d’élèves ;
- matricules réels ;
- montants réels de paiements ;
- coordonnées réelles de tuteurs ;
- documents confidentiels de l’établissement.

---

## 27. Documentation

Toute décision technique importante doit être documentée lorsqu’elle influence :

- l’architecture ;
- le modèle de données ;
- la sécurité ;
- les workflows métier ;
- les dépendances ;
- le déploiement.

Le `README.md` doit expliquer aux développeurs humains comment installer et lancer le projet.

Ce fichier `AGENT.md` contient les règles et le contexte destinés principalement aux agents de développement.

---

## 28. Gestion de l'incertitude

Lorsque l'information manque :

- ne pas inventer ;
- chercher dans le dépôt ;
- chercher dans la documentation du projet ;
- vérifier le code existant ;
- utiliser la documentation officielle de la technologie si nécessaire.

Si l'ambiguïté concerne une règle métier (ex. : calcul d’un solde, condition d’édition d’un reçu) ou une décision de périmètre :

> **STOP → signaler l’ambiguïté → demander validation.**

Il vaut mieux une question précise qu'une fonctionnalité parfaitement codée mais fausse.

---

## 29. Non-régression

Avant toute modification :

- comprendre le comportement actuel ;
- identifier les dépendances ;
- préserver les fonctionnalités existantes.

Après modification :

- exécuter les tests ;
- vérifier les modules affectés ;
- vérifier les permissions ;
- vérifier les migrations ;
- vérifier les parcours métier concernés.

Ne pas déclarer une tâche terminée uniquement parce que « le code compile ».

---

## 30. Règle finale

Pour chaque contribution, respecter cette chaîne :

```text
Spécification (BASE_CONNAISSANCE_IA_MERIBA_V2.md)
    ↓
Compréhension du besoin
    ↓
Modèle métier / UML (diagramme de classes, cas d’utilisation)
    ↓
Conception technique (Django, modèles, vues, services)
    ↓
Implémentation
    ↓
Tests
    ↓
Vérification sécurité
    ↓
Validation fonctionnelle
    ↓
Documentation
```

**Priorités absolues :**

1. exactitude fonctionnelle (respect des règles métier) ;
2. sécurité et confidentialité des données ;
3. intégrité des données (soldes, reçus, traçabilité) ;
4. cohérence avec le projet (périmètre, stack, architecture) ;
5. maintenabilité ;
6. performance ;
7. ergonomie ;
8. sophistication technique.

Le système doit rester simple, fiable et cohérent avec le besoin réel du Complexe Scolaire Meriba.
```