#!/bin/bash

echo "Waiting for PostgreSQL..."
# Print env vars for debug (you can disable in production)
echo "POSTGRES_USER=$POSTGRES_USER"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "POSTGRES_DB=$POSTGRES_DB"

# Wait until PostgreSQL is ready
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for database..."
  sleep 2
done

echo "PostgreSQL is up."

# Optionally regenerate models (disabled for now)
# if [ ! -f book/models.py ]; then
#   echo "Generating models with inspectdb..."
#   python manage.py inspectdb > book/models.py
# fi

# Ensure migrations are up to date
echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Applying migrations..."
python manage.py migrate --noinput

# Load seed data
echo "Seeding data from custom management command..."
# python manage.py load_seed_data

OR use raw SQL only once
if [ ! -f .seeded ]; then
  echo "Seeding database from init.sql..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -f init.sql && touch .seeded
fi
python manage.py collectstatic --noinput


# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn GutenbergDjango.wsgi:application --bind 0.0.0.0:8000
