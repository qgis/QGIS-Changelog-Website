from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Remove all tables that start with certification_, vota_, or lesson_"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute(
                """
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND (tablename LIKE 'certification\_%' OR tablename LIKE 'vota\_%' OR tablename LIKE 'lesson\_%')
      """
            )
            tables = [row[0] for row in cursor.fetchall()]

            if not tables:
                self.stdout.write(self.style.SUCCESS("No matching tables found."))
                return

            for table in tables:
                self.stdout.write(f"Dropping table: {table}")
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')

            self.stdout.write(self.style.SUCCESS(f"Dropped {len(tables)} tables."))
