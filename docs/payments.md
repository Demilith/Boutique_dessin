Stripe Connect (recommendation)
-------------------------------

Recommendation: use Stripe Connect (Express) for France.

Why:
- Stripe supports marketplaces and handles KYC, payouts, and European regulations.
- With Connect Express, each artist can have their own Stripe account and receive payouts directly.
- Your platform can take optional application fees/commissions.

High-level steps:
1. Create a Stripe platform account and enable Connect.
2. Use the backend endpoints to create a Stripe Express account for an artist (`POST /api/stripe/create-account/`).
3. Create an account link (`POST /api/stripe/create-account-link/`) and redirect the artist to Stripe onboarding.
4. Use webhooks to listen for `account.updated` to know when onboarding is complete.
5. When a customer pays, create a PaymentIntent and specify `transfer_data[destination]` to route funds to the connected account, or use Checkout Sessions with `payment_intent_data[transfer_data]`.

Notes:
- For development, use test keys in environment `STRIPE_SECRET_KEY`.
- In production, ensure your platform complies with EU/France tax and KYC requirements and configure webhooks securely.
