from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from base.tests.model_factories import ProjectF
from changes.tests.model_factories import CategoryF, EntryF, VersionF

DIRTY_DESCRIPTION = (
    'Adds a ruler tool.\n'
    '\n'
    '## AI tool usage\n'
    '- [ ] I used an AI tool.\n'
)


class CleanEntryBoilerplateTest(TestCase):
    def setUp(self):
        self.project = ProjectF.create()
        self.category = CategoryF.create(project=self.project)
        self.version = VersionF.create(project=self.project, name='3.40')
        self.other_version = VersionF.create(
            project=self.project, name='3.42')
        self.dirty = EntryF.create(
            description=DIRTY_DESCRIPTION,
            category=self.category,
            version=self.version,
        )
        self.clean = EntryF.create(
            description='Adds a scale bar.',
            category=self.category,
            version=self.version,
        )
        self.dirty_other_version = EntryF.create(
            description=DIRTY_DESCRIPTION,
            category=self.category,
            version=self.other_version,
        )

    def run_command(self, *args):
        out = StringIO()
        call_command('clean_entry_boilerplate', *args, stdout=out)
        return out.getvalue()

    def test_dry_run_reports_without_saving(self):
        for args in ((), ('--dry-run',)):
            with self.subTest(args=args):
                output = self.run_command(*args)
                self.assertIn('2 entries would change.', output)
                self.assertIn(self.dirty.title, output)
                self.assertNotIn(self.clean.title, output)
                self.dirty.refresh_from_db()
                self.assertEqual(self.dirty.description, DIRTY_DESCRIPTION)

    def test_apply_saves_cleaned_descriptions(self):
        output = self.run_command('--apply')
        self.assertIn('2 entries changed.', output)
        self.dirty.refresh_from_db()
        self.clean.refresh_from_db()
        self.assertEqual(self.dirty.description, 'Adds a ruler tool.')
        self.assertEqual(self.clean.description, 'Adds a scale bar.')

        self.assertIn('0 entries would change.', self.run_command())

    def test_version_slug_limits_the_entries(self):
        self.run_command('--apply', '--version-slug', self.version.slug)
        self.dirty.refresh_from_db()
        self.dirty_other_version.refresh_from_db()
        self.assertEqual(self.dirty.description, 'Adds a ruler tool.')
        self.assertEqual(
            self.dirty_other_version.description, DIRTY_DESCRIPTION)
