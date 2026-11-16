# coding=utf-8
"""A command to strip the PR template boilerplate from existing entries."""

from typing import Any

import reversion
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from changes.models import Entry
from changes.utils.github_pull_request import strip_pr_boilerplate


class Command(BaseCommand):
    """Remove the AI tool usage block and the template comment from entries.

    It only reports by default. Pass --apply to save the changes.
    """

    help = (
        'Remove the pull request template boilerplate from entry '
        'descriptions. Nothing is saved unless you pass --apply.'
    )

    def add_arguments(self, parser: CommandParser) -> None:
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument(
            '--dry-run',
            action='store_true',
            help='List the entries that would change. This is the default.',
        )
        mode.add_argument(
            '--apply',
            action='store_true',
            help='Save the cleaned descriptions.',
        )
        parser.add_argument(
            '--version-slug',
            help='Only check the entries of this version, for example 3-40.',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        entries = Entry.objects.exclude(description__isnull=True)
        if options['version_slug']:
            entries = entries.filter(version__slug=options['version_slug'])

        changes = []
        for entry in entries.iterator():
            cleaned = strip_pr_boilerplate(entry.description)
            if cleaned != entry.description:
                changes.append((entry, cleaned))
                self.stdout.write(f'Entry {entry.pk}: {entry.title}')

        if not options['apply']:
            self.stdout.write(
                f'{len(changes)} entries would change. '
                'Run again with --apply to save them.')
            return

        with transaction.atomic(), reversion.create_revision():
            reversion.set_comment('Removed the pull request template text.')
            for entry, cleaned in changes:
                entry.description = cleaned
                entry.save(update_fields=['description'])
        self.stdout.write(self.style.SUCCESS(
            f'{len(changes)} entries changed.'))
