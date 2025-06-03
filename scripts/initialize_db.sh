#!/bin/bash
# Database initialization script
set -e

# Wait for postgres to be ready
echo "Waiting for postgres..."
until PGPASSWORD=postgres psql -h db -U postgres -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - executing initialization"

# Run database migrations
cd /app
alembic upgrade head

# Create initial user if needed
python -m scripts.create_admin_user

echo "Database initialization complete!"
