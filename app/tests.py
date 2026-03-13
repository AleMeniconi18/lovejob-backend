from django.test import TestCase, Client
from django.urls import reverse


class SanityCheckTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_django_funziona(self):
        """Verifica che Django sia configurato correttamente"""
        self.assertTrue(True)

    def test_admin_raggiungibile(self):
        """Verifica che la pagina di login admin funzioni"""
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)


class APITest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_endpoint_non_autenticato_ritorna_401(self):
        response = self.client.get("/api/presenze/dipendenti/")
        self.assertEqual(response.status_code, 401)

    def test_login_con_credenziali_sbagliate(self):
        """Verifica che il login fallisca con credenziali errate"""
        response = self.client.post(
            "/api/auth/login/",
            {"username": "utente_inesistente", "password": "password_sbagliata"},
        )
        self.assertEqual(response.status_code, 400)
