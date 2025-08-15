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
    A->>A: Check account lock status
    alt Account locked
        A-->>F: Account locked error
        F-->>B: Show lockout message
    else Account active
        A->>A: Verify bcrypt password
        alt Invalid password
            A->>DB: Increment failed attempts
            A-->>F: Invalid credentials error
        else Valid password
            A->>DB: Reset failed attempts
            A->>A: Create access & refresh JWT
            A->>DB: Create user session
            A-->>F: {access, refresh} tokens
            F-->>B: Store tokens (secure storage)
        end
    end
    U->>B: Request protected resource
    B->>F: Send access token
    F->>A: GET /protected (Bearer token)
    A->>A: Validate token & role
    A-->>F: Protected data
    F-->>B: Render content
```

**Security considerations:**
- Passwords hashed with bcrypt before comparison.
- Account lockout after 5 failed login attempts for 30 minutes.
- Tokens have short-lived access and refresh expirations with secure storage and rotation.
- Role-based access control enforced on protected routes.
- HTTPS used between browser and frontend to prevent eavesdropping.
- Session tracking for security monitoring.

## Registration

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant F as Frontend
    participant A as Auth API
    participant DB as Database

    U->>B: Fill registration form
    B->>F: Client-side validation (real-time)
    F->>F: Password strength checking
    F->>F: Email format validation
    B->>F: Submit form (HTTPS)
    F->>A: POST /auth/register
    A->>A: Validate input (email, password, name, role)
    A->>A: Check password strength (8+ chars, mixed case, numbers, symbols)
    A->>A: Normalize email to lowercase
    A->>DB: Check email uniqueness
    alt Email exists
        A-->>F: Email already registered error
    else New email
        A->>A: Hash password with bcrypt
        A->>DB: Insert new user with security fields
        DB-->>A: User created with UUID
        A->>A: Create access & refresh JWT
        A->>DB: Create initial user session
        A-->>F: Registration success + tokens
        F-->>B: Auto-login user
        F-->>B: Redirect to dashboard/profile
    end
```

**Security considerations:**
- Emails normalized and stored in lowercase for consistency.
- Strong password requirements: minimum 8 characters, uppercase, lowercase, numbers, special characters.
- Passwords stored as bcrypt hashes with salt rounds.
- Terms of service and privacy policy acceptance tracked with timestamps.
- User profile completion status tracked.
- Password change timestamps for security auditing.
- Failed login attempts counter initialized to 0.
- Email verification status tracked (ready for future implementation).
- Auto-login after successful registration for better UX.

## Password Security Features

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth API
    participant DB as Database

    U->>F: Enter password during registration
    F->>F: Real-time strength validation
    alt Weak password
        F-->>U: Show strength indicator (red/yellow)
        F-->>U: Display requirements
    else Strong password
        F-->>U: Show strength indicator (green)
        F->>A: Submit registration
        A->>A: Server-side password validation
        A->>A: Check against common passwords
        A->>A: Check for repeated characters
        alt Password fails server validation
            A-->>F: Detailed validation error
        else Password passes
            A->>A: Hash with bcrypt
            A->>DB: Store user with security fields
        end
    end
```

## Account Security & Monitoring

- **Account Lockout**: Accounts lock automatically after 5 failed login attempts for 30 minutes.
- **Password Aging**: System tracks when passwords were last changed (ready for forced updates).
- **Session Management**: All user sessions are tracked with creation timestamps.
- **Audit Trail**: Registration includes terms acceptance timestamps and profile completion status.
- **Role-Based Access**: Users can register as students, instructors, or admins with appropriate permissions.

## Missing or Future Enhancements
- Email verification for new accounts (database fields ready).
- Multi-factor authentication.
- Secure refresh token rotation and revocation list.
- Password reset via email verification tokens.
- Advanced audit logging and security monitoring.
- Rate limiting on registration endpoints.
- CAPTCHA integration for bot prevention.
