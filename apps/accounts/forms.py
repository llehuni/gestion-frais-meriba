from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import Role, User


class LoginForm(forms.Form):
    use_required_attribute = False
    login = forms.CharField(label="Login", max_length=150, widget=forms.TextInput(attrs={"autofocus": True, "class": "input", "placeholder": "Ex: admin"}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Votre mot de passe"}))

    def clean(self):
        cleaned = super().clean()
        login_val = cleaned.get("login")
        password = cleaned.get("password")
        if login_val and password:
            try:
                user_obj = User.objects.get(login=login_val)
            except User.DoesNotExist:
                raise ValidationError("Login ou mot de passe incorrect.")
            if not user_obj.check_password(password):
                raise ValidationError("Login ou mot de passe incorrect.")
            if not user_obj.actif or not user_obj.is_active:
                raise ValidationError("Compte désactivé. Contacter l'administrateur.")
            # Vérification supplémentaire via authenticate pour cohérence backend
            user = authenticate(username=login_val, password=password)
            cleaned["user"] = user if user is not None else user_obj
        return cleaned


class UserCreateForm(UserCreationForm):
    use_required_attribute = False
    class Meta:
        model = User
        fields = ("login", "prenom", "nom", "email", "role", "actif")
        widgets = {
            "login": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: kabuya"}),
            "prenom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Marie"}),
            "nom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Kabuya"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "Ex: kabuya@meriba.cd"}),
            "role": forms.Select(attrs={"class": "select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prenom"].required = True
        self.fields["nom"].required = True
        self.fields["login"].help_text = "Unique, sans espaces."
        # password1/password2 issus de UserCreationForm
        self.fields["password1"].widget.attrs.update({"class": "input", "placeholder": "Min. 8 caractères"})
        self.fields["password2"].widget.attrs.update({"class": "input", "placeholder": "Confirmez le mot de passe"})


class UserUpdateForm(UserChangeForm):
    use_required_attribute = False
    # Retirer le champ password hashé en lecture seule par défaut, le gérer séparément
    password = None

    class Meta:
        model = User
        fields = ("login", "prenom", "nom", "email", "role", "actif")
        widgets = {
            "login": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: kabuya"}),
            "prenom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Marie"}),
            "nom": forms.TextInput(attrs={"class": "input", "placeholder": "Ex: Kabuya"}),
            "email": forms.EmailInput(attrs={"class": "input", "placeholder": "Ex: kabuya@meriba.cd"}),
            "role": forms.Select(attrs={"class": "select"}),
        }


class UserPasswordResetForm(forms.Form):
    use_required_attribute = False
    new_password1 = forms.CharField(label="Nouveau mot de passe", widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Nouveau mot de passe"}))
    new_password2 = forms.CharField(label="Confirmation", widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Confirmez le mot de passe"}))

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned
