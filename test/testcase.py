from django.contrib.auth.models import User
from django_dynamic_fixture import G
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase as DRFTestCase


class APITestCase(DRFTestCase):
    maxDiff = None

    def authorize(self, user=None):
        user = user or G(User)
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        return user

    def deauthorize(self):
        self.client.credentials()
