#!/bin/bash
set -e

# Create the pg_stat_statements extension for query performance monitoring
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable pg_stat_statements extension for query performance monitoring
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
    
    -- Reset statistics to start fresh
    SELECT pg_stat_statements_reset();
    
    -- Verify extension is loaded
    SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements';
EOSQL

echo "PostgreSQL performance monitoring extensions enabled successfully!"
