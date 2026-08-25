"""
Modèle Utilisateur — fidèle au diagramme de classes Meriba (AGENT.md §11, BASE §7).

Hiérarchie UML :
    Utilisateur (classe parente)
        ├── Administrateur
        ├── Directeur (Direction)
        ├── Secretaire
        └── Caissier

Implémentation Django : Single Table Inheritance + Proxy Models.
- Un seul modèle concret `User` (table accounts_user) porte tous les attributs communs.
- 4 proxy models reflètent l'héritage UML sans table supplémentaire.
- `role` matérialise le discriminant UML.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    ADMINISTRATEUR = "administrateur", _("Administrateur")
    DIRECTEUR = "directeur", _("Direction")
    SECRETAIRE = "secretaire", _("Secrétaire")
    CAISSIER = "caissier", _("Caissier")


login_validator = RegexValidator(
    regex=r"^[\w.@+-]+$",
    message=_("Le login ne peut contenir que lettres, chiffres et @/./+/-/_ ."),
)


class UserManager(BaseUserManager):
    """Manager pour Utilisateur (login = USERNAME_FIELD)."""

    def create_user(self, login, email=None, password=None, **extra_fields):
        if not login:
            raise ValueError("Le login est obligatoire.")
        email = self.normalize_email(email) if email else ""
        login = self.model.normalize_username(login)
        user = self.model(login=login, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, email=None, password=None, **extra_fields):
        extra_fields.setdefault("role", Role.ADMINISTRATEUR)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("actif", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser doit avoir is_superuser=True.")
        return self.create_user(login, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Utilisateur — classe parente UML.

    Attributs UML :
        id, login, prenom, nom, email, motDePasse (password haché), role, actif
    Méthodes UML :
        connecter(), deconnecter()  -> wrappers autour de django.contrib.auth
    """

    # id auto (BigAutoField via DEFAULT_AUTO_FIELD)
    login = models.CharField(
        _("login"),
        max_length=150,
        unique=True,
        validators=[login_validator],
        help_text=_("Identifiant unique de connexion."),
        error_messages={"unique": _("Ce login est déjà utilisé.")},
        db_index=True,
    )
    prenom = models.CharField(_("prénom"), max_length=150, blank=False)
    nom = models.CharField(_("nom"), max_length=150, blank=False)
    email = models.EmailField(_("adresse e-mail"), blank=True, db_index=True)
    # motDePasse -> AbstractBaseUser.password (haché, jamais en clair - AGENT §9)
    role = models.CharField(_("rôle"), max_length=20, choices=Role.choices, default=Role.SECRETAIRE)
    actif = models.BooleanField(
        _("actif"),
        default=True,
        help_text=_("Désactivé = compte bloqué sans suppression physique."),
    )
    # Champs Django requis
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # alias technique, synchronisé avec actif
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ["prenom", "nom"]

    class Meta:
        verbose_name = _("utilisateur")
        verbose_name_plural = _("utilisateurs")
        ordering = ["login"]

    def __str__(self) -> str:
        return f"{self.login} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        # Synchroniser actif <-> is_active (actif = champ métier UML)
        self.is_active = self.actif
        super().save(*args, **kwargs)

    # --- API compat Django admin ---
    @property
    def username(self):
        return self.login

    @property
    def first_name(self):
        return self.prenom

    @property
    def last_name(self):
        return self.nom

    def get_full_name(self):
        return f"{self.prenom} {self.nom}".strip()

    def get_short_name(self):
        return self.prenom

    # --- Méthodes UML ---
    def connecter(self, request=None):
        """UML connecter() — délègue à django.contrib.auth.login(request, self)."""
        if request is not None:
            from django.contrib.auth import login

            login(request, self)

    def deconnecter(self, request=None):
        """UML deconnecter() — délègue à django.contrib.auth.logout(request)."""
        if request is not None:
            from django.contrib.auth import logout

            logout(request)

    # --- Helpers rôles (RG-06) ---
    @property
    def is_administrateur(self):
        return self.role == Role.ADMINISTRATEUR

    @property
    def is_directeur(self):
        return self.role == Role.DIRECTEUR

    @property
    def is_secretaire(self):
        return self.role == Role.SECRETAIRE

    @property
    def is_caissier(self):
        return self.role == Role.CAISSIER


# --- Proxy models : héritage UML sans table supplémentaire ---


class AdministrateurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.ADMINISTRATEUR)


class Administrateur(User):
    """Proxy UML Administrateur."""

    objects = AdministrateurManager()

    class Meta:
        proxy = True
        verbose_name = _("administrateur")
        verbose_name_plural = _("administrateurs")

    # Méthodes UML documentées (signatures métier, corps minimal - AGENT §11)
    def gererClasse(self):
        return self.is_administrateur

    def gererTypeFrais(self):
        return self.is_administrateur

    def gererFrais(self):
        return self.is_administrateur

    def gererAnneeScolaire(self):
        return self.is_administrateur

    def gererUtilisateur(self):
        return self.is_administrateur


class DirecteurManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.DIRECTEUR)


class Directeur(User):
    """Proxy UML Directeur (Direction)."""

    objects = DirecteurManager()

    class Meta:
        proxy = True
        verbose_name = _("directeur")
        verbose_name_plural = _("directeurs")

    def consulterDetailPaiement(self):
        return self.role in [Role.DIRECTEUR, Role.ADMINISTRATEUR]

    def consulterTotalDu(self):
        return True

    def consulterSolde(self):
        return True

    def consulterArrieres(self):
        return True

    def consulterStatistiques(self):
        return self.is_directeur or self.is_administrateur


class SecretaireManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.SECRETAIRE)


class Secretaire(User):
    """Proxy UML Secretaire."""

    objects = SecretaireManager()

    class Meta:
        proxy = True
        verbose_name = _("secrétaire")
        verbose_name_plural = _("secrétaires")

    def enregistrerEleve(self):
        return self.is_secretaire or self.is_administrateur

    def consulterDetailPaiement(self):
        return True

    def consulterTotalDu(self):
        return True

    def consulterSolde(self):
        return True

    def consulterArrieres(self):
        return True


class CaissierManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=Role.CAISSIER)


class Caissier(User):
    """Proxy UML Caissier."""

    objects = CaissierManager()

    class Meta:
        proxy = True
        verbose_name = _("caissier")
        verbose_name_plural = _("caissiers")

    def enregistrerPaiement(self):
        return self.is_caissier

    def ajouterRecu(self):
        return self.is_caissier

    def consulterDetailPaiement(self):
        return True

    def consulterTotalDu(self):
        return True

    def consulterSolde(self):
        return True

    def consulterArrieres(self):
        return True
