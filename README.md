# Gutenberg Django API

This project is a Django-based API that provides book data similar to Project Gutenberg. It uses a PostgreSQL database, 
where the schema and data are initialized directly from a raw `.sql` file. Instead of writing models manually, 
Django's `inspectdb` command is used to auto-generate models based on the existing database schema. 
The entire application is containerized using Docker, with services defined via Docker Compose. 
A custom Bash script (`entry-point.sh`) ensures that the database is ready, applies migrations, generates models if not present, and runs the Django server.

To run the project locally, start by cloning the repository and switching to the `dev` branch:

```bash
git clone -b dev https://github.com/your-username/gutenberg-django.git
cd gutenberg-django
Create a .env file with the following environment variables for the PostgreSQL container:

env
POSTGRES_DB=gutenberg_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
Make sure the entry-point.sh file has Unix line endings (LF) and is executable:

bash
chmod +x entry-point.sh
Now you can build and run the project using Docker Compose:

bash
docker-compose up --build
This will start the PostgreSQL database, seed it with the .sql file, generate Django models using inspectdb, and start the Django development server at http://localhost:8000.

If you want to stop the project and remove all containers and volumes completely, use:

bash
docker-compose down --volumes --remove-orphans
This setup allows you to run the project without manual model creation or local database setup, using only Docker and the preloaded .sql schema.
