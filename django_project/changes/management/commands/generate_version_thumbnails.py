# coding=utf-8
"""Management command to backfill image_file_thumbnail for all Version records."""
from django.core.management.base import BaseCommand
from changes.models import Version


class Command(BaseCommand):
    help = (
        'Generate image_file_thumbnail for every Version that has an '
        'image_file but no thumbnail yet.  Pass --force to regenerate all '
        'thumbnails even when one already exists.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Regenerate thumbnails even when image_file_thumbnail already exists.',
        )

    def handle(self, *args, **options):
        force = options['force']
        qs = Version.objects.exclude(image_file='')
        if not force:
            qs = qs.filter(image_file_thumbnail='')

        total = qs.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nothing to do — all thumbnails are up to date.'))
            return

        self.stdout.write(f'Generating thumbnails for {total} version(s)…')

        ok = 0
        failed = 0
        for version in qs.iterator():
            try:
                version._generate_thumbnail()
                ok += 1
                self.stdout.write(f'  ✓  {version.name}  ({version.image_file.name})')
            except Exception as exc:
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f'  ✗  {version.name}: {exc}')
                )

        summary = f'Done — {ok} generated'
        if failed:
            summary += f', {failed} failed'
        self.stdout.write(self.style.SUCCESS(summary))
