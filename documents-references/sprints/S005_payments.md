# Sprint 5 — Payments (Stripe + PayPal, test)

## Goals
Checkout for paid courses or subscription. Test mode only.

## Data
- orders(id, user_id, amount_cents, currency, status enum['created','paid','failed','refunded'], provider enum['stripe','paypal'], created_at)
- order_items(id, order_id fk, course_id fk, price_cents, qty)
- user_courses(user_id, course_id, started_at, completed_at nullable)

## API
- POST /payments/stripe/checkout-session -> {url}
- POST /payments/stripe/webhook
- POST /payments/paypal/create-order -> {approve_url}
- POST /payments/paypal/webhook

## Rules
- On successful webhook, create user_courses row granting access.

## Acceptance
- Test transactions complete and access is granted.
