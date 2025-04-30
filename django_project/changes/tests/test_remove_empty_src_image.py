from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from changes.tests.model_factories import EntryF, CategoryF, VersionF
from base.tests.model_factories import ProjectF


class FixUrlImageEntryTest(TestCase):
    def setUp(self):
        description = (
            '<p>There was no way we ship <em>QGIS 3.14 '
            '"Temporal edition"</em> without temporal support '
            'to layouts:<img  src="" /></p>'
        )
        self.project = ProjectF.create()
        self.category = CategoryF.create(
            project=self.project,
            name=u'Custom Category',
        )
        self.version = VersionF.create(project=self.project)
        self.entry = EntryF.create(
            description=description,
            category=self.category,
            version=self.version,
        )
        self.entry.save()

    def test_command_output(self):
        out = StringIO()
        call_command('remove_empty_src_image', stdout=out)
        self.assertIn(
            'Remove img element in %s' % self.entry.title,
            out.getvalue())
