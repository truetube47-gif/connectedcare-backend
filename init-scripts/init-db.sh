#!/bin/bash
set -e

echo "Setting up pharmadbuser and pharmadb database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER pharmadbuser WITH ENCRYPTED PASSWORD '$POSTGRES_PASSWORD';
    CREATE DATABASE pharmadb;
    GRANT ALL PRIVILEGES ON DATABASE pharmadb TO pharmadbuser;
    ALTER USER pharmadbuser CREATEDB;
EOSQL

echo "Database setup complete!"