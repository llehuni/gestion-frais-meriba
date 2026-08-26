"""
Views authentification & gestion utilisateurs — RG-06/07/09.

- Login/Logout : tout utilisateur actif
- CRUD utilisateurs : Administrateur uniquement (AGENT.md §10)
- Dashboard : protégé, redirection par rôle si besoin
"""
import logging

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from .forms import LoginForm, UserCreateForm, UserPasswordResetForm, UserUpdateForm
from .models import Role, User
from .permissions import AdminRequiredMixin

logger = logging.getLogger(__name__)


# --- Authentification ---


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.cleaned_data["user"]
        login(request, user)
        logger.info("Connexion réussie login=%s ip=%s", user.login, request.META.get("REMOTE_ADDR"))
        messages.success(request, f"Bienvenue {user.get_full_name() or user.login}.")
        # RG-09 : journalisation connexion
        nxt = request.GET.get("next") or "accounts:dashboard"
        try:
            return redirect(nxt)
        except Exception:
            return redirect("accounts:dashboard")
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logger.info("Déconnexion login=%s", request.user.login)
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("accounts:login")


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    from apps.classes.models import Classe
    from apps.students.models import Eleve
    role = request.user.role
    # Données réelles pour vider les statiques
    ctx = {
        "role": role,
        "roles": Role.choices,
        "total_eleves": Eleve.objects.count(),
        "total_classes": Classe.objects.count(),
        "eleves_par_classe": Classe.objects.all().order_by("niveau", "section")[:6],
    }
    # Calcul simple des à jour / débiteurs si future app payments existe, sinon 0
    try:
        ctx["a_jour"] = Eleve.objects.count()  # placeholder
        ctx["debiteurs"] = 0
    except Exception:
        ctx["a_jour"] = 0
        ctx["debiteurs"] = 0
    return render(request, "accounts/dashboard.html", ctx)


# --- Gestion utilisateurs (Administrateur) ---


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().order_by("login")
        q = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role", "").strip()
        if q:
            qs = qs.filter(login__icontains=q) | qs.filter(prenom__icontains=q) | qs.filter(nom__icontains=q)
            qs = qs.distinct()
        if role in dict(Role.choices):
            qs = qs.filter(role=role)
        return qs

    def render_to_response(self, context, **response_kwargs):
        # HTMX : retourne uniquement le fragment table (AGENT.md §15)
        if self.request.headers.get("HX-Request") == "true" or self.request.META.get("HTTP_HX_REQUEST") == "true":
            return self.response_class(
                request=self.request,
                template="accounts/_user_table.html",
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )
        return super().render_to_response(context, **response_kwargs)


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Création utilisateur id=%s login=%s role=%s par %s", self.object.pk, self.object.login, self.object.role, self.request.user.login)
        messages.success(self.request, f"Utilisateur {self.object.login} créé.")
        return resp


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        resp = super().form_valid(form)
        logger.info("Modification utilisateur id=%s login=%s par %s", self.object.pk, self.object.login, self.request.user.login)
        messages.success(self.request, f"Utilisateur {self.object.login} mis à jour.")
        return resp


class UserToggleActiveView(AdminRequiredMixin, View):
    """Active/désactive sans suppression physique (RG-08). HTMX-aware."""

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        is_hx = request.headers.get("HX-Request") == "true" or request.META.get("HTTP_HX_REQUEST") == "true"
        if user.pk == request.user.pk:
            messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
            if is_hx:
                # Retourne la ligne inchangée avec message via header HX-Trigger
                resp = render(request, "accounts/_user_row.html", {"u": user})
                resp["HX-Trigger"] = "showMessage"
                return resp
            return redirect("accounts:user_list")
        user.actif = not user.actif
        user.save()
        logger.info("Toggle actif id=%s login=%s actif=%s par %s", user.pk, user.login, user.actif, request.user.login)
        messages.success(request, f"Utilisateur {user.login} {'activé' if user.actif else 'désactivé'}.")
        if is_hx:
            # Réponse fragment : ligne mise à jour avec badge et bouton reflétant l'état
            return render(request, "accounts/_user_row.html", {"u": user})
        return redirect("accounts:user_list")


class UserResetPasswordView(AdminRequiredMixin, View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordResetForm()
        return render(request, "accounts/user_reset_password.html", {"form": form, "target": user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            logger.info("Reset mot de passe id=%s login=%s par %s", user.pk, user.login, request.user.login)
            messages.success(request, f"Mot de passe de {user.login} réinitialisé.")
            return redirect("accounts:user_list")
        return render(request, "accounts/user_reset_password.html", {"form": form, "target": user})
