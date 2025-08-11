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

# Initialize main database if empty
if check_empty_db "$POSTGRES_DB"; then
  echo "Loading sample data..."
  
  # Create tables and load initial data
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
    -- Create users table
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      email VARCHAR(255) UNIQUE NOT NULL,
      hashed_password VARCHAR(255) NOT NULL,
      is_active BOOLEAN DEFAULT true,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Insert sample users (password is 'password123' hashed)
    INSERT INTO users (email, hashed_password) VALUES
      ('admin@example.com', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewE.yEr/Qw5.Hs2.'),
      ('user@example.com', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewE.yEr/Qw5.Hs2.');

    -- Create courses table
    CREATE TABLE IF NOT EXISTS courses (
      id SERIAL PRIMARY KEY,
      title VARCHAR(255) NOT NULL,
      description TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    -- Insert sample courses
    INSERT INTO courses (title, description) VALUES
      ('Introduction to Python', 'Learn the basics of Python programming language'),
      ('Web Development with FastAPI', 'Build modern web APIs with FastAPI framework'),
      ('Frontend Development with React', 'Learn to build user interfaces with React');

    -- Create enrollments table
    CREATE TABLE IF NOT EXISTS enrollments (
      id SERIAL PRIMARY KEY,
      user_id INTEGER REFERENCES users(id),
      course_id INTEGER REFERENCES courses(id),
      created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(user_id, course_id)
    );

    -- Create some sample enrollments
    INSERT INTO enrollments (user_id, course_id) VALUES
      (1, 1),
      (1, 2),
      (2, 1);
EOSQL

  echo "Sample data loaded successfully!"
else
  echo "Database already contains tables, skipping sample data..."
fi
