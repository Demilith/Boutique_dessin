# Stripe Webhook Testing (local)

This document explains how to test Stripe webhooks locally using the Stripe CLI.

1. Install Stripe CLI:

   - macOS (Homebrew): `brew install stripe/stripe-cli/stripe`\
   - Windows (Scoop/choco) or from https://stripe.com/docs/stripe-cli

2. Authenticate the CLI with your Stripe account:

```bash
stripe login
```

3. Run the local Django server (example):

```bash
python manage.py runserver 0.0.0.0:8000
```

4. Start listening and forward events to your local webhook endpoint (`/api/stripe/webhook/`):

```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

When the CLI starts it will print a `Webhook signing secret:` value (for example `whsec_...`). Copy that value and set it as the environment variable used by the Django app (`STRIPE_WEBHOOK_SECRET`) so the app can validate signatures.

5. Trigger a test `checkout.session.completed` event (or any other event):

```bash
stripe trigger checkout.session.completed
```

Note: `stripe trigger` will create simplified test objects. If you need a session tied to a specific product metadata (so the webhook creates an Order for your product), use the Admin API or create a Checkout Session from your frontend with the product metadata set, then complete the payment with Stripe test cards.

6. Example: Creating a checkout session from the backend for testing (curl):

```bash
curl -X POST "http://localhost:8000/api/stripe/checkout/1/" -H "Content-Type: application/json"
```

Adjust `1` for your product id.

7. Verify webhook logs and that `Order` records are created in the Django admin or database.

Troubleshooting
- If webhook verification fails, ensure `STRIPE_WEBHOOK_SECRET` matches the value printed by `stripe listen`.
- Use `stripe logs tail` to stream events and see delivery attempts.
