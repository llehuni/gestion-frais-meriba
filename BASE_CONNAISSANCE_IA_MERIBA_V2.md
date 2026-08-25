# Base de connaissance IA — Gestion des frais scolaires du Complexe Scolaire Meriba

## 1. Identité et compréhension globale

**Objet :** système d'information destiné à automatiser la gestion des frais scolaires du Complexe Scolaire Meriba.

Le système actuel est principalement manuel : registres physiques, cahiers, fiches papier, reçus manuscrits et parfois feuilles de calcul non centralisées. Le projet vise à remplacer ce fonctionnement par un dispositif numérique centralisé, sécurisé et fiable.

### Problèmes identifiés
- lenteur dans l'enregistrement et la recherche ;
- erreurs de saisie et de calcul ;
- difficulté de suivi des situations financières ;
- risque de perte/détérioration des documents ;
- production lente de rapports financiers ;
- faible traçabilité des opérations ;
- manque de communication entre secrétariat, caisse et direction ;
- inadéquation aux exigences modernes de rapidité, sécurité, accessibilité et aide à la décision.

### Objectif général
Optimiser la gestion financière scolaire par un système intégré, fiable et sécurisé permettant le suivi transparent des frais scolaires, l'informatisation des paiements et la production de rapports financiers utiles à la prise de décision.

### Objectifs spécifiques
- centraliser les données financières ;
- informatiser le suivi des paiements ;
- améliorer la transparence ;
- réduire les erreurs humaines ;
- produire des rapports financiers ;
- renforcer la sécurité des données ;
- améliorer la planification budgétaire.

### Périmètre
Le projet couvre le **cycle primaire** : élèves, classes, années scolaires, frais, paiements, reçus, soldes/arriérés, rapports financiers et utilisateurs.

### Hors périmètre
- autres cycles ;
- gestion pédagogique ;
- ressources humaines ;
- comptabilité complète ;
- bibliothèques ;
- internats ;
- paiements électroniques/bancaires.

---

## 2. Cahier des charges

### Fonction 1 — Enregistrement des élèves
**Acteur principal :** Secrétaire administratif.

Données citées : matricule, nom, post-nom, prénom, sexe, date de naissance, classe, année scolaire, coordonnées du tuteur.

Contraintes : utilisateur autorisé, champs obligatoires, matricule unique et prévention des doublons.

### Fonction 2 — Paramétrage des frais et des classes
**Acteur cité :** Administrateur.

Gestion : classes de 1ère à 6ème primaire, années scolaires, types de frais et montants. Types cités : inscription, scolarité, examens, bulletin, autres contributions.

Contraintes : définition par classe ou globalement, traçabilité/validation des modifications, interdiction de supprimer une classe ou un frais déjà associé à des opérations.

### Fonction 3 — Enregistrement des paiements et édition des reçus
**Acteur principal :** Chargé des Finances / Caissier.

Processus : rechercher l'élève → sélectionner le frais → saisir montant/date/mode de paiement → enregistrer → mettre à jour le solde → générer le reçu numéroté.

Contraintes : montant strictement positif, reçu unique contenant identité, motif, montant, date et agent.

### Fonction 4 — Consultation et suivi financier
Consultation du détail des paiements, montant total dû, solde restant et arriérés. Recherche par nom, matricule ou classe. Accès dépendant du profil ; lecture seule pour les agents non autorisés à modifier.

### Fonction 5 — Production des rapports
Rapports : recettes journalières, hebdomadaires, mensuelles, annuelles ; élèves à jour ; débiteurs ; recettes par type de frais ; statistiques par classe. Export PDF/Excel si nécessaire.

### Fonction 6 — Gestion des utilisateurs
Création, modification, blocage, suppression de comptes, attribution de rôles et contrôle des droits. Authentification obligatoire et historique des connexions/actions pour audit.

---

## 3. Besoins non fonctionnels

### Sécurité
Authentification, contrôle d'accès, hachage des mots de passe, protection contre injections SQL et XSS, sessions sécurisées, HTTPS/TLS en déploiement en ligne, sauvegardes et journalisation des actions sensibles.

### Fiabilité
Validation des saisies, contrôles d'intégrité et transactions sécurisées.

### Performance
Réponses rapides lors des recherches et enregistrements.

### Ergonomie
Interface intuitive pour les utilisateurs non informaticiens.

### Maintenabilité et évolutivité
Code modulaire et capacité à évoluer avec l'augmentation du nombre d'élèves et de nouvelles fonctionnalités.

### Sauvegarde et traçabilité
Sauvegarde automatique/récupération et journalisation des actions.

---

## 4. Acteurs et responsabilités

| Acteur | Responsabilités/fonctions documentées |
|---|---|
| **Secrétaire Administratif** | Enregistrer, modifier et consulter les élèves ; gérer classes et années scolaires |
| **Chargé des Finances / Caissier** | Enregistrer paiements, éditer reçus, consulter situations, suivre impayés, rechercher |
| **Direction** | Consulter rapports, tableaux de bord et indicateurs ; suivre impayés/tendances ; valider paramètres généraux |
| **Administrateur du système** | Gérer comptes, rôles, frais, années, maintenance, sauvegardes et journaux d'audit |

Le document présente le **Tuteur comme acteur externe** du système.

---

## 5. Processus métiers

1. **Inscription / Réinscription** : collecte, saisie, matricule, affectation à une classe.
2. **Paramétrage des frais** : définition des types et montants par niveau/classe.
3. **Perception des paiements** : recherche, saisie, mise à jour du solde, reçu.
4. **Consultation financière** : soldes et historique.
5. **Suivi des impayés** : identification des retards pour relance et mesures administratives.
6. **Production de rapports** : recettes, débiteurs, statistiques.
7. **Contrôle/audit** : journalisation et traçabilité.

---

## 6. Diagrammes de cas d'utilisation

Le document présente un **diagramme de cas d'utilisation global** puis six regroupements :

- **A. Enregistrement des élèves**
- **B. Paramétrages de frais et des classes**
- **C. Système de paiement**
- **D. Système de consultation**
- **E. Système de production**
- **F. Système de gestion des utilisateurs**

### Limite importante
Le texte extrait du document confirme les intitulés ci-dessus, mais ne restitue pas toutes les informations graphiques des diagrammes. La base ne doit donc pas inventer :

- les associations exactes acteur/cas ;
- les relations `include` ;
- les relations `extend` ;
- les généralisations ;
- les noms de sous-cas qui ne sont visibles que dans le graphique.

Pour une transcription exacte, il faut analyser les pages graphiques du document.

---

## 7. Diagramme de classes

## 1. Hiérarchie des utilisateurs

Le système utilise l'héritage pour factoriser les caractéristiques communes aux différents utilisateurs.

### Utilisateur

Classe parente contenant les attributs communs :

- `id`
- `login`
- `prenom`
- `nom`
- `email`
- `motDePasse`
- `role`
- `actif`

Méthodes :

- `connecter()`
- `deconnecter()`

### Administrateur

Hérite de `Utilisateur`.

Méthodes :

- `gererClasse()`
- `gererTypeFrais()`
- `gererFrais()`
- `gererAnneeScolaire()`
- `gererUtilisateur()`

### Directeur

Hérite de `Utilisateur`.

Méthodes :

- `consulterDetailPaiement()`
- `consulterTotalDu()`
- `consulterSolde()`
- `consulterArrieres()`
- `consulterStatistiques()`

### Secretaire

Hérite de `Utilisateur`.

Méthodes :

- `consulterDetailPaiement()`
- `consulterTotalDu()`
- `consulterSolde()`
- `consulterArrieres()`
- `enregistrerEleve()`

### Caissier

Hérite de `Utilisateur`.

Méthodes :

- `enregistrerPaiement()`
- `ajouterRecu()`
- `consulterDetailPaiement()`
- `consulterTotalDu()`
- `consulterSolde()`
- `consulterArrieres()`

---

## 2. Entités du domaine scolaire

### Eleve

Attributs :

- `id`
- `nom`
- `prenom`
- `dateNaissance`
- `sexe`
- `adresse`
- `matricule`

Méthode :

- `getMatricule()`

### Classe

Attributs :

- `id`
- `nom`
- `section`
- `niveau`

Méthode :

- `getListeEleve()`

### AnneeScolaire

Attributs :

- `id`
- `libelle`
- `dateDebut`
- `dateFin`

### TypeDeFrais

Attributs :

- `id`
- `libelle`
- `description`

Méthode :

- `getFrais()`

### Frais

Représente le montant d'un type de frais pour une classe donnée.

Attributs :

- `id`
- `montant`
- `dateCreation`

Méthode :

- `getType()`

---

## 3. Entité centrale : Paiement

`Paiement` constitue l'entité pivot des opérations financières.

Attributs :

- `id`
- `montantPaye`
- `datePaiement`
- `modePaiement`
- `montantTotalDu`
- `solde`
- `arrieres`

Méthodes :

- `calculerTotalDu()`
- `calculerSolde()`
- `calculerArrieres()`

---

## 4. Relations et cardinalités

### Eleve — Paiement

Un élève peut effectuer zéro ou plusieurs paiements.

Eleve 1 ───── 0..* Paiement

## Paiement — AnneeScolaire

Un paiement concerne une seule année scolaire.

Paiement 0..* ───── 1 AnneeScolaire

## Eleve — Classe

Un élève appartient à une classe et une classe regroupe plusieurs élèves.

Eleve 0..* ───── 1 Classe

## Classe — Frais

Une classe peut être associée à plusieurs frais et un frais peut concerner plusieurs classes.

Classe 0..* ───── 0..* Frais

## Frais — TypeDeFrais

Un frais correspond à un seul type de frais et un type de frais peut être associé à plusieurs frais.

Frais 0..* ───── 1 TypeDeFrais

## Caissier — Paiement

Un Caissier peut enregistrer zéro à plusieurs paiements, tandis qu’un Paiement est enregistré par un seul Caissier.

Caissier 1 ───── enregistrer ───── 0..* Paiement

Dans la section Relations et cardinalités, ajoute :

Cette relation est particulièrement pertinente pour la **traçabilité des opérations financières**, puisque le système doit pouvoir identifier l’agent ayant effectué chaque enregistrement.

## 5. Vue conceptuelle
                    ┌─────────────────┐
                    │   Utilisateur   │
                    ├─────────────────┤
                    │ id              │
                    │ login           │
                    │ prenom          │
                    │ nom             │
                    │ email           │
                    │ motDePasse      │
                    │ role            │
                    │ actif           │
                    ├─────────────────┤
                    │ connecter()     │
                    │ deconnecter()   │
                    └────────┬────────┘
                             │ héritage
             ┌───────────────┼───────────────┬───────────────┐
             │               │               │               │
     ┌───────▼──────┐ ┌──────▼───────┐ ┌─────▼──────┐ ┌──────▼─────┐
     │Administrateur│ │  Directeur   │ │ Secretaire │ │  Caissier  │
     └──────────────┘ └──────────────┘ └────────────┘ └────────────┘


┌─────────┐       0..*      1       ┌──────────┐
│  Eleve  │─────────────────────────│  Classe  │
└────┬────┘                         └────┬─────┘
     │ 1                                  │ 0..*
     │                                    │
     │ 0..*                         ┌─────▼─────┐
┌────▼─────┐                        │   Frais   │
│ Paiement │                        └─────┬─────┘
└────┬─────┘                              │ 0..*
     │                                    │
     │ 0..*                               │ 1
     │                               ┌────▼──────────┐
┌────▼────────────┐                  │ TypeDeFrais   │
│ AnneeScolaire   │                  └───────────────┘
└─────────────────┘

Les éléments ci-dessus reprennent les informations fournies dans le complément du diagramme de classes. Les cardinalités sont conservées telles qu'indiquées.

---

## 8. Choix de technologies

| Technologie | Rôle documenté |
|---|---|
| **Python 3** | Développement du backend avec Django |
| **Django** | Framework backend |
| **Jinja2** | Moteur de templating Python pour les pages HTML dynamiques |
| **MySQL** | SGBD de stockage et gestion des données |
| **HTMX** | Mises à jour dynamiques depuis le HTML, sans JavaScript pour ces interactions |
| **Bulma CSS** | Framework CSS moderne et responsive pour l'interface |
| **Git** | Contrôle de version et collaboration |

### Stack de référence
```text
Backend          : Python 3 + Django
Templates        : Jinja2
Interactions      : HTMX
UI / CSS          : Bulma CSS
Base de données  : MySQL
Versionnement     : Git
```

---

## 9. Architecture

### Architecture générale
Architecture **client-serveur** avec trois couches logicielles :

### Couche Présentation
Interface entre les acteurs et l'application : tableaux de bord, formulaires, reçus et saisies utilisateur.

### Couche Applicative / Métier
Cœur du système : requêtes, règles métier, authentification et échanges avec la base via l'ORM.

### Couche Données / Persistance
Stockage, récupération et intégrité des données financières et administratives.

### Architecture physique
- **Serveur** : application Django + base MySQL, en local ou dans le Cloud.
- **Postes clients** : secrétariat, caisse, direction.
- **Réseau** : LAN stable ; HTTPS/SSL/TLS pour protéger les communications.

---

## 10. Priorité des fonctionnalités

| Fonction | Priorité |
|---|---|
| Enregistrement des élèves | Très élevée |
| Enregistrement des paiements / édition des reçus | Très élevée |
| Consultation et suivi financier | Élevée |
| Production des rapports | Moyenne |
| Paramétrage des frais et classes | Moyenne |
| Gestion des utilisateurs | Moyenne |

---

## 11. Règles métier à respecter

- **RG-01** : un élève possède un matricule unique.
- **RG-02** : les champs obligatoires doivent être renseignés avant validation.
- **RG-03** : un matricule dupliqué doit être refusé.
- **RG-04** : un paiement nul ou négatif doit être refusé.
- **RG-05** : un reçu possède un numéro unique.
- **RG-06** : le solde doit être mis à jour en temps réel après un paiement.
- **RG-07** : les droits dépendent du rôle de l'utilisateur.
- **RG-08** : les modifications et opérations sensibles doivent être tracées.
- **RG-09** : une classe ou un frais déjà associé à des opérations ne doit pas être supprimé.
- **RG-10** : les connexions et actions doivent pouvoir être auditées.

---

## 12. Méthodologie

Le projet adopte **Unified Process (UP)** et **Unified Modeling Language (UML)**.

Les quatre phases documentées sont :

1. **Inception** : compréhension du contexte, parties prenantes, périmètre, problématique et objectifs.
2. **Élaboration** : analyse du système existant et collecte des besoins.
3. **Construction** : conception détaillée et développement itératif avec validations intermédiaires.
4. **Transition** : tests, validation, formation, déploiement, maintenance et sauvegarde.

---

## 13. Contraintes organisationnelles

- formation du personnel ;
- protocole interne de perception des frais ;
- protocole de délivrance des reçus ;
- gestion des impayés ;
- politique d'accès et de confidentialité ;
- conservation transitoire des documents papier ;
- coordination entre secrétariat, caisse et direction ;
- accès aux heures d'ouverture, sauf maintenance administrateur.

---

## 14. Points sensibles à conserver tels quels

### 14.1. Python confirmé
La version actuelle du document indique explicitement dans les contraintes logicielles : **Python, HTML, CSS, JavaScript**, et la section « Choix des technologies » précise **Python 3 + Django + Jinja2 + MySQL + HTMX + Bulma CSS + Git**.

### 14.2. Jinja2
Le document écrit correctement **Jinja2** dans la version actuelle.

L'agent IA ne doit pas fusionner ou séparer ces profils sans nouvelle décision fonctionnelle.

---

## 15. Instructions générales pour l'agent IA

```text
Tu travailles sur le projet de gestion des frais scolaires du Complexe Scolaire Meriba.

Référence fonctionnelle : cette base de connaissance et le document source du projet.

Règles :
1. Le périmètre principal est la gestion des frais scolaires du cycle primaire.
2. Ne pas ajouter de module hors périmètre sans demande explicite.
3. Les fonctions centrales sont : élèves, classes, années scolaires, frais, paiements, reçus, situations financières, impayés, rapports et utilisateurs.
4. Respecter les acteurs et responsabilités documentés.
5. Respecter les règles de validation, d'unicité, de sécurité et de traçabilité.
6. Utiliser la stack de référence : Python 3, Django, Jinja2, HTMX, Bulma CSS, MySQL et Git.
7. Respecter l'architecture client-serveur à trois couches.
8. Ne pas inventer le contenu des diagrammes UML graphiques qui n'est pas disponible dans le texte.
9. Distinguer les informations explicitement documentées des décisions nouvelles proposées pendant la conception.
10. En cas d'absence d'une information, signaler qu'elle n'est pas spécifiée au lieu de l'inventer.
```

---

# FIN
