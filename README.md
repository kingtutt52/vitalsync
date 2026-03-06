# VitalSync — AI-Powered Health Optimization Platform (MVP)

A full-stack health platform with a Python/FastAPI backend, PostgreSQL database, and Flutter mobile app.

---

## Repo Structure

```
vitalsync/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # auth.py, health.py, files.py, ai.py, billing.py
│   │   ├── core/           # config.py, security.py
│   │   ├── db/             # base.py, session.py
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # health_score.py, file_parser.py, storage.py, stripe_service.py
│   │   └── tests/          # pytest unit tests
│   ├── migrations/         # Alembic migrations
│   ├── storage/            # Uploaded files (gitignored in prod)
│   ├── seed.py             # Creates demo user + sample data
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── mobile/
│   ├── lib/
│   │   ├── core/           # theme, router, constants
│   │   ├── data/           # API clients + data models
│   │   ├── presentation/   # screens + Riverpod providers
│   │   └── main.dart
│   ├── pubspec.yaml
│   └── .env.example
├── infra/
│   └── nginx.conf          # Production reverse proxy example
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

- Docker + Docker Compose
- Flutter SDK ≥ 3.3 (for mobile)
- Stripe account (test mode) — optional for payment testing

---

## 1. Run the Backend (Docker)

```bash
# Clone and enter the repo
cd vitalsync

# Copy env file
cp backend/.env.example backend/.env
# Edit backend/.env with your Stripe keys (leave others as-is for local dev)

# Start Postgres + FastAPI (runs migrations + seed automatically)
docker compose up --build
```

The API will be available at **http://localhost:8000**
API docs (Swagger UI): **http://localhost:8000/docs**

**Test user created by seed script:**
- Email: `demo@vitalsync.dev`
- Password: `VitalSync123!`
- Tier: Premium Lite (can generate health plans)

---

## 2. Run Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest app/tests/ -v
```

---

## 3. Run Backend Locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # then edit DATABASE_URL to point to your Postgres

alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

---

## 4. Run the Flutter App

```bash
cd mobile
cp .env.example .env

# Android emulator: API_BASE_URL=http://10.0.2.2:8000
# iOS simulator: API_BASE_URL=http://localhost:8000
# Physical device: API_BASE_URL=http://<your-machine-LAN-IP>:8000

flutter pub get
flutter run
```

---

## 5. Stripe Webhook Local Testing

Install the Stripe CLI:
```bash
# macOS
brew install stripe/stripe-cli/stripe

# or download from https://stripe.com/docs/stripe-cli
```

Forward webhooks to your local server:
```bash
stripe listen --forward-to localhost:8000/billing/webhook
```

The CLI will print a webhook signing secret — paste it into `backend/.env` as `STRIPE_WEBHOOK_SECRET`.

Trigger a test event:
```bash
stripe trigger customer.subscription.created
```

---

## 6. Setting Up Stripe Products

In your Stripe test dashboard:

1. Create a Product called "VitalSync Subscriptions"
2. Add three prices:
   - Premium Lite: $9.99/month, recurring
   - Vital+: $29.99/month, recurring
   - VitalPro: $79.99/month, recurring
3. Copy the price IDs into `backend/.env`:
   ```
   STRIPE_PRICE_PREMIUM_LITE=price_xxx
   STRIPE_PRICE_VITAL_PLUS=price_xxx
   STRIPE_PRICE_VITAL_PRO=price_xxx
   ```

---

## API Endpoints Summary

| Method | Endpoint | Auth | Tier |
|--------|----------|------|------|
| POST | /auth/register | No | — |
| POST | /auth/login | No | — |
| GET | /auth/me | Yes | Any |
| POST | /health/bloodwork | Yes | Free+ |
| GET | /health/bloodwork | Yes | Free+ |
| POST | /health/lifestyle | Yes | Free+ |
| GET | /health/lifestyle | Yes | Free+ |
| GET | /health/summary | Yes | Free+ |
| POST | /ai/generate-plan | Yes | Premium Lite+ |
| POST | /files/bloodwork-upload | Yes | Premium Lite+ |
| POST | /files/genetics-upload | Yes | VitalPro |
| GET | /files/ | Yes | Any |
| POST | /billing/create-checkout-session | Yes | Any |
| GET | /billing/status | Yes | Any |
| POST | /billing/webhook | No (Stripe sig) | — |

---

## MVP Demo Script

### Full Click-Through Flow

**1. Register a new account**
- Open the app → tap "Create Account"
- Enter name, email, password → submit
- You land on the Dashboard

**2. Log bloodwork**
- Tap "Bloodwork" quick action (or drawer)
- Enter: Vitamin D = 24, LDL = 138, A1c = 5.8, CRP = 2.1
- Set date → Save

**3. Log lifestyle**
- Tap "Lifestyle"
- Enter: Sleep = 6.5, Steps = 6200, Stress = 7
- Save

**4. Generate Health Plan**
- On Dashboard, tap "Generate / Refresh Health Plan"
- Your Health Score appears (expect ~50-65 range with the sample data)
- Scroll down to see your personalised Action Plan items

**5. Upload a bloodwork file**
- Tap "Upload File" → "Select Bloodwork File"
- Pick any PDF or image from your device
- Confirmation appears

**6. View subscription tiers**
- Open drawer → Subscription
- See all four tiers; tap "Upgrade to Premium Lite"
- Stripe checkout opens in browser (test mode — use card 4242 4242 4242 4242)

**7. Test with seed user via API**
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@vitalsync.dev","password":"VitalSync123!"}'

# Use the returned token
TOKEN="<paste token here>"

# Generate health plan
curl -X POST http://localhost:8000/ai/generate-plan \
  -H "Authorization: Bearer $TOKEN"
```

---

## Architecture Notes

- **Rules engine** (`backend/app/services/health_score.py`): deterministic, auditable, easily extended. Each rule is a function returning a delta + insight + action. To add ML: replace `compute_health_plan()` while keeping the same `ScoringOutput` interface.
- **File storage** (`backend/app/services/storage.py`): local filesystem for dev. To migrate to S3, replace `save_file()` with a Boto3 call — no other code changes needed.
- **Tier gating** (`backend/app/api/deps.py`): `require_tier()` is a FastAPI dependency factory. Add it to any route in one line.
- **State management** (Flutter): Riverpod `StateNotifier` for all mutable state, `FutureProvider` for read-only async data.
