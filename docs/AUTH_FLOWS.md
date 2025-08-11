# Authentication & Registration Flows

This document illustrates how the X University application handles user authentication, authorization, and registration. Sequence diagrams use Mermaid notation.

## Login: Authentication & Authorization

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Frontend
    participant A as Auth API
    participant DB as Database

    U->>B: Enter email & password
    B->>F: Submit login form (HTTPS)
    F->>A: POST /auth/login
    A->>DB: Lookup user by email
    DB-->>A: User record
    A->>A: Verify bcrypt password
    A->>A: Create access & refresh JWT
    A-->>F: {access, refresh} tokens
    F-->>B: Store tokens (secure storage)
    U->>B: Request protected resource
    B->>F: Send access token
    F->>A: GET /protected (Bearer token)
    A->>A: Validate token & role
    A-->>F: Protected data
    F-->>B: Render content
```

**Security considerations:**
- Passwords hashed with bcrypt before comparison.
- Tokens have short-lived access and refresh expirations with secure storage and rotation【F:README.md†L569-L572】
- Role-based access control enforced on protected routes【F:README.md†L574-L577】
- HTTPS used between browser and frontend to prevent eavesdropping.

## Registration

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Frontend
    participant A as Auth API
    participant DB as Database

    U->>B: Fill registration form
    B->>F: Submit form (HTTPS)
    F->>A: POST /auth/register
    A->>A: Validate input (email, password, name)
    A->>A: Hash password with bcrypt
    A->>DB: Insert new user
    DB-->>A: User created
    A-->>F: Registration success (+ tokens)
    F-->>B: Show confirmation
```

**Security considerations:**
- Emails normalized and stored in lowercase【F:documents-references/sprints/S001_auth.md†L18-L18】
- Passwords must be at least 8 characters and stored as bcrypt hashes【F:documents-references/sprints/S001_auth.md†L18-L18】
- Tokens issued only after successful validation.

## Missing or Future Enhancements
- Email verification for new accounts.
- Multi-factor authentication.
- Account lockout and rate limiting to mitigate brute-force attacks.
- Secure refresh token rotation and revocation list.
- Audit logging and security monitoring.
