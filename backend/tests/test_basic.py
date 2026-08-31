from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from shop.models import ArtistProfile, Product


class BasicTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_create_product(self):
        # register
        res = self.client.post('/api/register/', {'username': 'alice', 'email': 'a@example.com', 'password': 'pass'})
        self.assertEqual(res.status_code, 200)
        access = res.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        # create product
        res = self.client.post('/api/products/', {'title': 'Art', 'description': 'Nice', 'price_cents': 1000, 'stock': 5})
        self.assertIn(res.status_code, (200, 201))
        product = Product.objects.first()
        self.assertIsNotNone(product)
