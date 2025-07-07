FROM python:3.11

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the pg_isready utility
RUN apt-get update \
    && apt-get install -y postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . /code

COPY entry-point.sh /code/entry-point.sh
RUN chmod +x /code/entry-point.sh

