#!/bin/bash

echo "Waiting for PostgreSQL..."

until python -c "import socket; socket.create_connection(('${POSTGRES_HOST}', ${POSTGRES_PORT}), timeout=1)" 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL is up."

# Continue your tasks...
python manage.py migrate

if [ ! -f books/models.py ]; then
  echo "Generating models with inspectdb..."
  python manage.py inspectdb > book/models.py
fi

# ✅ Run SQL seed script only if a marker doesn't exist
if [ ! -f .seeded ]; then
  echo "Seeding database from init.sql..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f init.sql && touch .seeded
fi
echo "Starting Gunicorn..."
gunicorn GutenbergDjango.wsgi:application --bind 0.0.0.0:8000
exec
