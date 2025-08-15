# X University Database Documentation

## PostgreSQL

### Main Database (xu2)
Primary database for the application with comprehensive user management and security features.

#### Implemented Tables

##### Users Table (`users`)
Core user authentication and profile management with security features:

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'student' CHECK (role IN ('admin', 'instructor', 'student')),
    is_active BOOLEAN DEFAULT true,
    
    -- Security fields
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP NULL,
    password_changed_at TIMESTAMP DEFAULT now(),
    
    -- Profile and compliance
    terms_accepted BOOLEAN DEFAULT false,
    terms_accepted_at TIMESTAMP NULL,
    privacy_policy_accepted BOOLEAN DEFAULT false,
    profile_completed BOOLEAN DEFAULT false,
    
    -- Email verification (ready for implementation)
    email_verified BOOLEAN DEFAULT false,
    email_verification_token VARCHAR NULL,
    email_verification_sent_at TIMESTAMP NULL,
    
    -- Audit timestamps
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);
```

**Security Features:**
- Account lockout after 5 failed login attempts (30-minute lockout)
- Password change tracking for security auditing
- Terms of service and privacy policy acceptance tracking
- Email verification readiness (tokens and timestamps prepared)
- Role-based access control with three user types

##### Sessions Table (`sessions`)
User session management for security and tracking:

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    last_accessed_at TIMESTAMP DEFAULT now(),
    user_agent TEXT,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL
);
```

**Features:**
- Device and IP tracking for security monitoring
- Session expiration management
- Support for multiple concurrent sessions per user
- Session revocation capabilities

#### Planned Tables (to be implemented):
- `courses` - Course catalog and management
- `lessons` - Individual lesson content and structure
- `enrollments` - Student course enrollments with progress tracking
- `progress` - Detailed learning progress and completion tracking
- `payments` - Payment processing and subscription management

### Database Security Features

#### Password Security
- **bcrypt hashing**: All passwords stored with bcrypt salt rounds
- **Password requirements**: 8+ characters, mixed case, numbers, symbols
- **Password aging**: Tracking of password change dates for security policies
- **Common password prevention**: Server-side validation against weak passwords

#### Account Protection
- **Automated lockout**: 5 failed attempts triggers 30-minute lockout
- **Failed attempt tracking**: Counter reset on successful login
- **Account monitoring**: Support for security event logging

#### Compliance & Legal
- **Terms acceptance**: Timestamped records of terms acceptance
- **Privacy policy**: Separate tracking of privacy policy acceptance
- **Profile completion**: Status tracking for user onboarding

### Migrations
Managed through Alembic with comprehensive schema evolution:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Check current revision
alembic current

# Rollback
alembic downgrade -1

# View migration history
alembic history --verbose
```

#### Recent Migration Files
- `6e7ad66a2f10_initial_auth_tables.py` - Initial user and session tables
- `1692902edebf_update_users_table_to_uuid_and_add_.py` - Enhanced user model with security fields

### Database Performance
Configured with optimizations for development and production:

- **Connection pooling**: SQLAlchemy async connection management
- **Query optimization**: Indexes on frequently queried fields (email, user_id)
- **Performance monitoring**: pg_stat_statements enabled for query analysis
- **Connection limits**: Configured max_connections for stability

## Database Schema Reference

### Table Definitions

#### Users Table (`users`)

| Column Name | Data Type | Constraints | Index | Description |
|-------------|-----------|-------------|-------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | PRIMARY | Unique user identifier |
| `email` | VARCHAR | UNIQUE, NOT NULL | UNIQUE | User email address (normalized to lowercase) |
| `full_name` | VARCHAR | NOT NULL | - | User's full display name |
| `password_hash` | VARCHAR | NOT NULL | - | bcrypt hashed password |
| `role` | VARCHAR | DEFAULT 'student', CHECK (role IN ('admin', 'instructor', 'student')) | INDEX | User role for authorization |
| `is_active` | BOOLEAN | DEFAULT true | INDEX | Account activation status |
| `failed_login_attempts` | INTEGER | DEFAULT 0 | - | Failed login counter for security |
| `locked_until` | TIMESTAMP | NULL | INDEX | Account lockout expiration time |
| `password_changed_at` | TIMESTAMP | DEFAULT now() | - | Last password change for security auditing |
| `terms_accepted` | BOOLEAN | DEFAULT false | - | Terms of service acceptance |
| `terms_accepted_at` | TIMESTAMP | NULL | - | Terms acceptance timestamp |
| `privacy_policy_accepted` | BOOLEAN | DEFAULT false | - | Privacy policy acceptance |
| `profile_completed` | BOOLEAN | DEFAULT false | INDEX | Profile completion status |
| `email_verified` | BOOLEAN | DEFAULT false | INDEX | Email verification status |
| `email_verification_token` | VARCHAR | NULL | - | Token for email verification |
| `email_verification_sent_at` | TIMESTAMP | NULL | - | Email verification request timestamp |
| `created_at` | TIMESTAMP | DEFAULT now() | INDEX | Account creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT now() | - | Last profile update timestamp |

**Indexes:**
- `users_pkey` (PRIMARY): `id`
- `users_email_key` (UNIQUE): `email`
- `users_role_idx` (INDEX): `role`
- `users_is_active_idx` (INDEX): `is_active`
- `users_locked_until_idx` (INDEX): `locked_until`
- `users_profile_completed_idx` (INDEX): `profile_completed`
- `users_email_verified_idx` (INDEX): `email_verified`
- `users_created_at_idx` (INDEX): `created_at`

#### Sessions Table (`sessions`)

| Column Name | Data Type | Constraints | Index | Description |
|-------------|-----------|-------------|-------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | PRIMARY | Unique session identifier |
| `user_id` | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | INDEX (FK) | Reference to user account |
| `is_active` | BOOLEAN | DEFAULT true | INDEX | Session activation status |
| `created_at` | TIMESTAMP | DEFAULT now() | INDEX | Session creation timestamp |
| `last_accessed_at` | TIMESTAMP | DEFAULT now() | INDEX | Last session access time |
| `user_agent` | TEXT | NULL | - | Browser/client user agent string |
| `ip_address` | INET | NULL | INDEX | Client IP address for security tracking |
| `expires_at` | TIMESTAMP | NOT NULL | INDEX | Session expiration timestamp |

**Indexes:**
- `sessions_pkey` (PRIMARY): `id`
- `sessions_user_id_idx` (INDEX): `user_id` (Foreign Key)
- `sessions_is_active_idx` (INDEX): `is_active`
- `sessions_created_at_idx` (INDEX): `created_at`
- `sessions_last_accessed_at_idx` (INDEX): `last_accessed_at`
- `sessions_ip_address_idx` (INDEX): `ip_address`
- `sessions_expires_at_idx` (INDEX): `expires_at`

### Planned Tables

#### Courses Table (`courses`) - To Be Implemented

| Column Name | Data Type | Constraints | Index | Description |
|-------------|-----------|-------------|-------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | PRIMARY | Unique course identifier |
| `title` | VARCHAR | NOT NULL | INDEX | Course title |
| `description` | TEXT | NULL | - | Course description |
| `instructor_id` | UUID | REFERENCES users(id) | INDEX (FK) | Course instructor |
| `is_published` | BOOLEAN | DEFAULT false | INDEX | Course publication status |
| `created_at` | TIMESTAMP | DEFAULT now() | INDEX | Course creation timestamp |
| `updated_at` | TIMESTAMP | DEFAULT now() | - | Last course update |

#### Enrollments Table (`enrollments`) - To Be Implemented

| Column Name | Data Type | Constraints | Index | Description |
|-------------|-----------|-------------|-------|-------------|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | PRIMARY | Unique enrollment identifier |
| `user_id` | UUID | REFERENCES users(id) ON DELETE CASCADE | INDEX (FK) | Student user reference |
| `course_id` | UUID | REFERENCES courses(id) ON DELETE CASCADE | INDEX (FK) | Course reference |
| `enrolled_at` | TIMESTAMP | DEFAULT now() | INDEX | Enrollment timestamp |
| `completed_at` | TIMESTAMP | NULL | INDEX | Course completion timestamp |
| `progress_percentage` | INTEGER | DEFAULT 0, CHECK (progress_percentage >= 0 AND progress_percentage <= 100) | INDEX | Course completion percentage |
| `is_active` | BOOLEAN | DEFAULT true | INDEX | Enrollment status |

**Composite Indexes (Planned):**
- `enrollments_user_course_unique` (UNIQUE): `user_id, course_id`
- `enrollments_user_active_idx` (INDEX): `user_id, is_active`
- `enrollments_course_active_idx` (INDEX): `course_id, is_active`

### Database Relationships

```
users (1) ←→ (N) sessions
    ↓ (1)
    ↓
    ↓ (N) enrollments (N) ←→ (1) courses
    ↓
users (instructors) (1) ←→ (N) courses
```

### Query Performance Notes

#### Most Frequent Queries
1. **User Authentication**: `SELECT * FROM users WHERE email = ?`
   - Uses: `users_email_key` (UNIQUE index)
   - Performance: O(1) lookup

2. **Session Validation**: `SELECT * FROM sessions WHERE id = ? AND is_active = true AND expires_at > now()`
   - Uses: `sessions_pkey`, `sessions_is_active_idx`, `sessions_expires_at_idx`
   - Performance: O(1) lookup with condition filtering

3. **User Session Lookup**: `SELECT * FROM sessions WHERE user_id = ? AND is_active = true`
   - Uses: `sessions_user_id_idx`, `sessions_is_active_idx`
   - Performance: O(log n) with composite filtering

4. **Account Security**: `SELECT locked_until, failed_login_attempts FROM users WHERE id = ?`
   - Uses: `users_pkey`
   - Performance: O(1) lookup

#### Index Maintenance
- Indexes are automatically maintained by PostgreSQL
- Regular `ANALYZE` commands keep statistics current
- Query performance monitoring via `pg_stat_statements`

## Neo4j (Optional)

### Learning Path Graph
Used to represent course prerequisites and learning paths.

#### Node Types:
- Course
- Topic
- Skill
- Learning Objective

#### Relationships:
- PREREQUISITE_OF
- LEADS_TO
- REQUIRES
- TEACHES

### Configuration
- Bolt port: 7687
- HTTP port: 7474
- Browser interface: http://localhost:7474
- Default credentials in dev: neo4j/devpass

### Usage
Neo4j is optional and can be disabled by setting `ENABLE_NEO4J=false` in `.env`


todo:
- add audit log for user logins and interactions