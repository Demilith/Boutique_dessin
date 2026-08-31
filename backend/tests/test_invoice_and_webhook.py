from django.test import TestCase, Client
from django.contrib.auth.models import User
from shop.models import ArtistProfile, Product, Order
from shop.utils import generate_invoice_pdf
from unittest.mock import patch
from django.urls import reverse
import io

class InvoiceGenerationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='artist1', email='artist@example.com', password='pass')
        self.artist = ArtistProfile.objects.create(user=self.user, display_name='Artist One')
        self.product = Product.objects.create(artist=self.artist, title='Test Product', price_cents=1500, stock=5)

    def test_generate_invoice_pdf_returns_buffer(self):
        order = Order.objects.create(product=self.product, buyer_email='buyer@example.com', amount_cents=1500)
        buf = generate_invoice_pdf(order)
        self.assertIsNotNone(buf)
        self.assertTrue(hasattr(buf, 'read'))
        data = buf.read(4)
        self.assertTrue(len(data) > 0)

class WebhookProcessingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='pass')
        self.artist_user = User.objects.create_user(username='artist2', email='artist2@example.com', password='pass')
        self.artist = ArtistProfile.objects.create(user=self.artist_user, display_name='Artist Two')
        self.product = Product.objects.create(artist=self.artist, title='Webhook Product', price_cents=2000, stock=2)

    @patch('shop.views.stripe')
    @patch('shop.views.upload_buffer_to_s3')
    def test_webhook_creates_order_and_sets_user(self, mock_upload, mock_stripe):
        # Mock stripe.Webhook.construct_event to return a fake checkout.session.completed event
        fake_session = {
            'metadata': {'product_id': str(self.product.id)},
            'amount_total': 2000,
            'payment_intent': 'pi_12345',
            'customer_details': {'email': 'buyer@example.com'}
        }
        mock_stripe.Webhook.construct_event.return_value = {'type': 'checkout.session.completed', 'data': {'object': fake_session}}
        mock_upload.return_value = None

        url = reverse('stripe-webhook')
        resp = self.client.post(url, data=b'{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='sig')
        self.assertEqual(resp.status_code, 200)
        order = Order.objects.filter(stripe_payment_intent='pi_12345').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.amount_cents, 2000)
        self.assertIsNotNone(order.user)
        self.assertEqual(order.user.email, 'buyer@example.com')
