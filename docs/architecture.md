# Architecture

The browser speaks only to the versioned FastAPI REST API. The API owns authentication, authorization, pricing, availability, inventory holds, state transitions and persistence. PostgreSQL is the system of record; `SELECT ... FOR UPDATE` is used while choosing physical rooms, with a recommended production exclusion constraint for a final database-level overlap guard.

`Booking` transitions `pending_payment → confirmed → checked_in → checked_out`, or `pending_payment/confirmed → cancelled`. The payment state is separate: a payment begins `created` and becomes `paid` only after verified provider confirmation. The local mock provider verifies synchronously; Razorpay production adapters must validate webhook signatures and use provider event IDs as idempotency keys.

Staff access is explicitly role based through `user_roles`, optionally hotel-scoped. Customers are constrained to their own bookings. Monetary fields are `Numeric`, timestamps are UTC, and booked nightly prices are snapshots in `booking_rooms` and `booking_price_items`.
