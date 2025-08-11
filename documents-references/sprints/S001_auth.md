# Sprint 1 — Auth and user accounts

## Goals
JWT auth. Registration, login, logout, refresh. RBAC: student, admin.

## Data (Postgres)
- users(id uuid pk, email unique not null, password_hash, role, full_name, created_at, updated_at)
- sessions(id uuid pk, user_id fk, refresh_token_hash, user_agent, ip, expires_at, created_at)

## API
- POST /auth/register {email,password,full_name}
- POST /auth/login {email,password} -> {access,refresh}
- POST /auth/refresh {refresh}
- POST /auth/logout
- GET /users/me

## Rules
- Password >= 8 chars, bcrypt. Email lowercased unique. JWT via jose. Access TTL 30m, Refresh TTL 7d.

## Frontend
- Forms with zod validation. Axios interceptors. Protected routes.

## Tests
- Register, login, logout, refresh, me. Invalid creds. Duplicate email.
