from django.core.management.base import BaseCommand
from changes.models import Entry

class Command(BaseCommand):
    help = 'Fix broken entries by removing <p> and </p> tags from descriptions'

    def handle(self, *args, **kwargs):
        entries = Entry.objects.all()
        for entry in entries:
            if entry.description and '<p>' in entry.description:
                entry.description = entry.description.replace('<p>', '').replace('</p>', '')
                entry.save()
        self.stdout.write(self.style.SUCCESS('Successfully fixed broken entries'))