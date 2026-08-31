Deployment guide (Docker)
-------------------------

This repo includes Dockerfiles and a `docker-compose.yml` for a simple containerized deployment.

Basic steps (local):

```bash
docker-compose up --build
```

Production notes:
- Use a managed Postgres database; update `DATABASE_URL` accordingly.
- Set secure `DJANGO_SECRET_KEY` and the environment variables for Stripe and SMTP.
- Run migrations on deploy: `python manage.py migrate`.
- Configure a real file storage (S3) by setting `USE_S3=True` and AWS credentials.
- Set up HTTPS and domain routing for frontend and backend. You can use a reverse proxy (NGINX) or host the frontend on a CDN.

Stripe and webhooks:
- Configure `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in your production environment.
- Use Stripe CLI or the dashboard to register your webhook endpoint and verify signatures.

Scaling:
- Consider separating services into distinct hosts: backend behind an app server (gunicorn) and a load balancer, frontend served by CDN, and media on S3.
