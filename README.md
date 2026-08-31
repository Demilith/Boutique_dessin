Boutique Dessin

Monorepo for a multi-artist web shop where artists can create private accounts, list artworks, manage stock, and customize their public pages.

Overview
- Backend: Node.js + Express API (auth, product management)
- Frontend: Vue 3 + Vite (customer-facing gallery and artist dashboard)
- Database: Prisma ORM (SQLite for development, Postgres recommended for production)
- Payments: Recommend Stripe Connect (each artist receives payouts to their own account)

Quick start (development)

1. Install dependencies for backend and frontend:

```bash
cd backend
npm install
cd ../frontend
npm install
```

2. Start backend and frontend (run in separate terminals):

```bash
cd backend
npm run dev

cd frontend
npm run dev
```

3. See frontend at http://localhost:5173 by default.

Next steps
- Set up a production database (Postgres) and update `DATABASE_URL`.
- Create a Stripe Connect account for platform onboarding (see `docs/payments.md`).
- Create a GitHub repository and push this project (see instructions below).

Docker / Deploy

Run with docker-compose for a local deployment:

```bash
docker-compose up --build
```

This will start Postgres, the Django backend (port 8000), and the frontend (port 8080).

CI

A basic GitHub Actions workflow is included in `.github/workflows/ci.yml` which installs backend dependencies, runs migrations, and builds the frontend on push/PR.

GitHub push example

```bash
git init
git add .
git commit -m "Initial scaffold"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```
