#!/bin/bash

echo "Waiting for PostgreSQL..."
# TEMP DEBUG: print vars
echo "POSTGRES_USER=$POSTGRES_USER"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "POSTGRES_DB=$POSTGRES_DB"
# until python -c "import socket; socket.create_connection(('${POSTGRES_HOST}', ${POSTGRES_PORT}), timeout=1)" 2>/dev/null; do
#   sleep 1
# done
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for database..."
  sleep 2
done


echo "PostgreSQL is up."



if [ ! -f books/models.py ]; then
  echo "Generating models with inspectdb..."
  python manage.py inspectdb > book/models.py
fi
python manage.py makemigrations
# Continue your tasks...
python manage.py migrate
echo "Loading seed data from init.sql..."

# if [ ! -f .seeded ]; then
#   echo "Seeding database from init.sql..."
#   PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -f init.sql && touch .seeded
# fi
echo "Starting Gunicorn..."
gunicorn GutenbergDjango.wsgi:application --bind 0.0.0.0:8000
exec
