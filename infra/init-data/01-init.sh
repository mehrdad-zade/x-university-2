#!/bin/bash
set -e

# Wait for the database to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for database to be ready..."
  sleep 2
done

# Create test database if it doesn't exist
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tc "SELECT 1 FROM pg_database WHERE datname = 'xu2_test'" | grep -q 1 || \
psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE xu2_test"

# Function to check if the database is empty
check_empty_db() {
  local count=$(psql -U "$POSTGRES_USER" -d "$1" -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
  [ "$count" -eq 0 ]
}

echo "Database initialized - schema and user creation will be handled by Alembic migrations and init_db.py"
echo "Skipping old sample data creation to prevent conflicts with modern migration system"

# NOTE: This init script previously created users and tables directly in SQL.
# However, this conflicts with the Alembic migration system and init_db.py script
# which handle proper schema creation and user initialization.
# 
# The application now uses:
# 1. Alembic migrations for database schema (proper column names, UUIDs, etc.)
# 2. init_db.py for creating default users with correct password hashing and roles
#
# This prevents conflicts between old SQL-based init and new migration-based init.
