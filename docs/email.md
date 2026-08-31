SMTP / Email configuration
-------------------------

This project uses the console email backend by default in development. To enable SMTP in production, set the following environment variables:

- `SMTP_HOST` — e.g. `smtp.gmail.com` or your provider
- `SMTP_PORT` — default `587`
- `SMTP_USER` — SMTP username
- `SMTP_PASSWORD` — SMTP password
- `SMTP_USE_TLS` — `True` or `False`
- `DEFAULT_FROM_EMAIL` — default sender address

When configured, the app will send HTML invoice emails to buyers and notification emails to artists upon successful purchases.
