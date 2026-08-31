# Backend (Django)

This directory contains a Django project (development scaffold).

Quickstart

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

3. Start dev server:

```bash
python manage.py runserver
```

API endpoints (development):
- `GET /api/products/` — list products
- `GET /api/artists/` — list artists and their products
