from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Administrateur, Caissier, Directeur, Role, Secretaire, User

UserModel = get_user_model()


class UserModelTest(TestCase):
    def test_create_user_hache_mot_de_passe(self):
        u = User.objects.create_user(login="jdoe", prenom="John", nom="Doe", password="StrongPass123", role=Role.SECRETAIRE)
        self.assertNotEqual(u.password, "StrongPass123")
        self.assertTrue(u.check_password("StrongPass123"))
        self.assertEqual(u.role, Role.SECRETAIRE)
        self.assertTrue(u.actif)
        self.assertTrue(u.is_active)

    def test_matricule_login_unique(self):
        User.objects.create_user(login="dup", prenom="A", nom="B", password="x12345678")
        with self.assertRaises(Exception):
            User.objects.create_user(login="dup", prenom="C", nom="D", password="y12345678")

    def test_actif_sync_is_active(self):
        u = User.objects.create_user(login="sync", prenom="S", nom="S", password="x12345678", actif=False)
        self.assertFalse(u.is_active)
        u.actif = True
        u.save()
        u.refresh_from_db()
        self.assertTrue(u.is_active)

    def test_proxy_managers(self):
        User.objects.create_user(login="admin1", prenom="A", nom="A", password="x12345678", role=Role.ADMINISTRATEUR)
        User.objects.create_user(login="sec1", prenom="S", nom="S", password="x12345678", role=Role.SECRETAIRE)
        self.assertEqual(Administrateur.objects.count(), 1)
        self.assertEqual(Secretaire.objects.count(), 1)
        self.assertEqual(Directeur.objects.count(), 0)
        self.assertEqual(Caissier.objects.count(), 0)

    def test_methodes_uml_roles(self):
        admin = User.objects.create_user(login="adm", prenom="A", nom="A", password="x12345678", role=Role.ADMINISTRATEUR)
        caissier = User.objects.create_user(login="cais", prenom="C", nom="C", password="x12345678", role=Role.CAISSIER)
        self.assertTrue(Administrateur.objects.get(pk=admin.pk).gererUtilisateur())
        self.assertTrue(Caissier.objects.get(pk=caissier.pk).enregistrerPaiement())
        self.assertFalse(caissier.is_administrateur)


class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(login="admin", prenom="Admin", nom="Meriba", password="Admin123!", role=Role.ADMINISTRATEUR, is_staff=True)
        self.secretaire = User.objects.create_user(login="sec", prenom="Sec", nom="Retariat", password="Sec123!", role=Role.SECRETAIRE)
        self.caissier = User.objects.create_user(login="caisse", prenom="Caisse", nom="Test", password="Caisse123!", role=Role.CAISSIER)
        self.directeur = User.objects.create_user(login="dir", prenom="Dir", nom="Ection", password="Dir123!", role=Role.DIRECTEUR)

    def test_login_success(self):
        resp = self.client.post(reverse("accounts:login"), {"login": "admin", "password": "Admin123!"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:dashboard"), resp.url)

    def test_login_fail(self):
        resp = self.client.post(reverse("accounts:login"), {"login": "admin", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "incorrect")

    def test_login_inactive_refused(self):
        self.secretaire.actif = False
        self.secretaire.save()
        resp = self.client.post(reverse("accounts:login"), {"login": "sec", "password": "Sec123!"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "désactivé")

    def test_dashboard_requires_login(self):
        resp = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp.url)

    def test_user_list_admin_only(self):
        # admin ok
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(resp.status_code, 200)
        # secretaire interdit -> 403
        self.client.force_login(self.secretaire)
        resp = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(resp.status_code, 403)
        # caissier interdit
        self.client.force_login(self.caissier)
        resp = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(resp.status_code, 403)
        # directeur interdit
        self.client.force_login(self.directeur)
        resp = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(resp.status_code, 403)

    def test_user_create_admin_only(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("accounts:user_create"),
            {"login": "newuser", "prenom": "New", "nom": "User", "email": "new@test.com", "role": Role.CAISSIER, "actif": True, "password1": "ComplexPass123!", "password2": "ComplexPass123!"},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(login="newuser").exists())

    def test_toggle_active_blocks_self(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse("accounts:user_toggle_active", args=[self.admin.pk]))
        self.assertEqual(resp.status_code, 302)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.actif)  # pas désactivé

    def test_csrf_protection_on_login(self):
        # Client enforce_csrf_checks
        csrf_client = Client(enforce_csrf_checks=True)
        resp = csrf_client.post(reverse("accounts:login"), {"login": "admin", "password": "Admin123!"})
        self.assertEqual(resp.status_code, 403)
