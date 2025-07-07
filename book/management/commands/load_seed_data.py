from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Seed the database from init.sql'

    def handle(self, *args, **kwargs):
        sql_path = 'book/init.sql'  # Update if path differs

        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        with connection.cursor() as cursor:
            cursor.execute(sql)

        self.stdout.write(self.style.SUCCESS('Successfully loaded init.sql'))
