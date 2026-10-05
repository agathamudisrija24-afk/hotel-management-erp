# Hotel Management and Online Booking System

An end-to-end hotel booking baseline with Next.js, FastAPI, SQLAlchemy and PostgreSQL. It includes live hotel data, secured tokens, physical-room availability, expiring holds, server-side prices, mock payments, cancellation/refunds, customer bookings, receptionist stay processing, roles, audit-ready entities and a seeded demo.

## Run locally

1. Start Docker Desktop (verify with `docker info`).
2. Optionally copy `.env.example` to `.env` and set a durable `SECRET_KEY` (Compose has safe development defaults, so this is not required to start locally).
3. Run `docker compose up --build`.
4. Open `http://localhost:3000`; API OpenAPI docs are at `http://localhost:8000/api/docs`.

The startup seed is development-only and creates these credentials (all password `DemoPass123!`): `admin@hotel.example`, `customer@hotel.example`, `reception@hotel.example`, and `housekeeping@hotel.example`.

## Verification

Run backend tests from `backend/` with `pytest`. Frontend production validation is `npm install && npm run build` from `frontend/`.

## Production notes

Set secure secrets/environment values, restrict CORS, terminate TLS, run Alembic revisions (see `backend/migrations/README.md`), use PostgreSQL and add the recommended physical-room date-range exclusion constraint. Configure the Razorpay adapter with real signature verification and SMTP/S3 adapters before selecting non-mock providers. The mock provider is deliberately only for development/testing and does not contact an external processor.

## Key API paths

- `POST /api/v1/auth/register`, `POST /auth/login`, `GET /auth/me`
- `GET /api/v1/hotels`, `GET /hotels/{id}`, `GET /availability`
- `POST /api/v1/bookings`, `GET /bookings`, `POST /bookings/{id}/cancel`
- `POST /api/v1/payments/initiate`, `POST /payments/{id}/verify`, `POST /payments/webhook`
- `POST /api/v1/staff/bookings/{id}/check-in`, `.../check-out`

See [the architecture document](docs/architecture.md) for invariants and boundary design.
