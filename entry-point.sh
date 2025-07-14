#!/bin/bash

echo "Waiting for PostgreSQL..."
until python -c "import socket; socket.create_connection(('db', 5432), timeout=1)" 2>/dev/null; do
  sleep 1
done

echo "PostgreSQL is up."

# Run migrations
python manage.py migrate

# # Generate models if not exists
# if [ ! -f books/models.py ]; then
#   echo "Generating models with inspectdb..."
#   python manage.py inspectdb > books/models.py
# fi

# Start the server
python manage.py runserver 0.0.0.0:8000
