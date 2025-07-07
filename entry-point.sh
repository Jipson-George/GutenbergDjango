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

gunicorn GutenbergDjango.wsgi:application --bind 0.0.0.0:8000
exec
