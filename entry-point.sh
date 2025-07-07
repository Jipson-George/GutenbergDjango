#!/bin/bash

echo "Waiting for PostgreSQL..."

until python -c "import socket; socket.create_connection(('db', 5432), timeout=1)" 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL is up."

# Continue your tasks...
python manage.py migrate

if [ ! -f books/models.py ]; then
  echo "Generating models with inspectdb..."
  python manage.py inspectdb > book/models.py
fi

python manage.py runserver 0.0.0.0:8000
