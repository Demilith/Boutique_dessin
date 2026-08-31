"""
Create a Stripe Checkout Session using the Stripe secret key from env.
Requires: pip install stripe
Usage:
  python tools/create_stripe_checkout.py --product-id 1 --success-url http://localhost:3000/success --cancel-url http://localhost:3000/cancel
"""
import os
import stripe
import argparse

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

parser = argparse.ArgumentParser()
parser.add_argument('--product-id', type=int, required=True)
parser.add_argument('--price-cents', type=int, default=1000)
parser.add_argument('--currency', type=str, default='eur')
parser.add_argument('--success-url', type=str, required=True)
parser.add_argument('--cancel-url', type=str, required=True)
parser.add_argument('--destination-account', type=str, default=None, help='Connected Stripe account ID to transfer funds to')
args = parser.parse_args()

if not stripe.api_key:
    print('STRIPE_SECRET_KEY not set in environment')
    raise SystemExit(1)

line_items = [{
    'price_data': {
        'currency': args.currency,
        'product_data': {
            'name': f'Product {args.product_id}'
        },
        'unit_amount': args.price_cents,
    },
    'quantity': 1,
}]

payment_intent_data = None
if args.destination_account:
    payment_intent_data = {
        'transfer_data': {'destination': args.destination_account}
    }

session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=line_items,
    mode='payment',
    success_url=args.success_url,
    cancel_url=args.cancel_url,
    payment_intent_data=payment_intent_data,
    metadata={'product_id': str(args.product_id)}
)

print('Checkout session created:')
print(session.url)
