from django.core.management.base import BaseCommand
from shop.models import Order
import stripe
from django.conf import settings

class Command(BaseCommand):
    help = 'Reconcile orders with Stripe to ensure payments match records'

    def handle(self, *args, **options):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        pending = Order.objects.filter(fulfilled=True)
        for o in pending:
            try:
                if not o.stripe_payment_intent:
                    self.stdout.write(f'Order {o.id} has no payment intent')
                    continue
                pi = stripe.PaymentIntent.retrieve(o.stripe_payment_intent)
                status = pi.get('status')
                self.stdout.write(f'Order {o.id}: Stripe status {status}')
            except Exception as e:
                self.stdout.write(f'Error reconciling order {o.id}: {e}')
