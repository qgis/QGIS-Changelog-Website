# coding=utf-8
"""Tests for models."""
from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from changes.tests.model_factories import (
    CategoryF,
    EntryF,
    VersionF
)
from base.tests.model_factories import ProjectF


class TestCategoryCRUD(TestCase):
    """
    Tests search models.
    """

    def setUp(self):
        """
        Sets up before each test
        """
        self.project = ProjectF.create()

    def test_Category_create(self):
        """
        Tests Category model creation
        """
        model = CategoryF.create(
            project=self.project
        )

        # check if PK exists
        self.assertTrue(model.pk is not None)

        # check if name exists
        self.assertTrue(model.name is not None)

    def test_Category_read(self):
        """
        Tests Category model read
        """
        model = CategoryF.create(
            name=u'Custom Category',
            project=self.project
        )

        self.assertTrue(model.name == 'Custom Category')
        self.assertTrue(model.slug == 'custom-category')

    def test_Category_update(self):
        """
        Tests Category model update
        """
        model = CategoryF.create(
            project=self.project
        )
        new_model_data = {
            'name': u'New Category Name',
            'description': u'New description',
            'private': True,
        }
        model.__dict__.update(new_model_data)
        model.save()

        # check if updated
        for key, val in new_model_data.items():
            self.assertEqual(model.__dict__.get(key), val)

    def test_Category_delete(self):
        """
        Tests Category model delete
        """
        model = CategoryF.create(
            project=self.project
        )

        model.delete()

        # check if deleted
        self.assertTrue(model.pk is None)


class TestEntryCRUD(TestCase):
    """
    Tests search models.
    """

    def setUp(self):
        """
        Sets up before each test
        """
        self.project = ProjectF.create()
        self.category = CategoryF.create(
            project=self.project
        )
        self.version = VersionF.create(
            project=self.project
        )

    def test_Entry_create(self):
        """
        Tests Entry model creation
        """
        model = EntryF.create(
            category=self.category,
            version=self.version,
        )

        # check if PK exists
        self.assertTrue(model.pk is not None)

        # check if name exists
        self.assertTrue(model.title is not None)

    def test_Entry_read(self):
        """
        Tests Entry model read
        """
        model = EntryF.create(
            title=u'Custom Entry 1',
            developed_by=u'Tim',
            category=self.category,
            version=self.version,
        )

        self.assertTrue(model.title == 'Custom Entry 1')
        self.assertTrue(model.slug == 'custom-entry-1')
        self.assertTrue(model.developer_info_html() == '')

        model = EntryF.create(
            title=u'Custom Entry 2',
            developed_by=u'Tim',
            developer_url='',
            category=self.category,
            version=self.version,
        )
        self.assertTrue(
            model.developer_info_html() == 'This feature was '
                                           'developed by Tim ')

        model = EntryF.create(
            title=u'Custom Entry 3',
            developed_by=u'Tim',
            developer_url=u'https://github.com/timlinux',
            category=self.category,
            version=self.version,
        )
        self.assertTrue(
            model.developer_info_html() == 'This feature was '
                                           'developed by [Tim]'
                                           '(https://github.com/timlinux)')

    def test_Entry_update(self):
        """
        Tests Entry model update
        """
        model = EntryF.create(
            category=self.category,
            version=self.version,
        )
        new_model_data = {
            'name': u'New Entry Name',
            'description': u'New description',
            'approved': False,
            'private': True,
        }
        model.__dict__.update(new_model_data)
        model.save()

        # check if updated
        for key, val in new_model_data.items():
            self.assertEqual(model.__dict__.get(key), val)

    def test_Entry_delete(self):
        """
        Tests Entry model delete
        """
        model = EntryF.create(
            category=self.category,
            version=self.version,
        )

        model.delete()

        # check if deleted
        self.assertTrue(model.pk is None)


class TestVersionCRUD(TestCase):
    """
    Tests search models.
    """

    def setUp(self):
        """
        Sets up before each test
        """
        self.project = ProjectF.create()

    def test_Version_create(self):
        """
        Tests Version model creation
        """
        model = VersionF.create(
            project=self.project,
        )

        # check if PK exists
        self.assertTrue(model.pk is not None)

        # check if name exists
        self.assertTrue(model.name is not None)

    def test_Version_read(self):
        """
        Tests Version model read
        """
        model = VersionF.create(
            description=u'Test Description',
            project=self.project,
        )
        self.assertTrue(model.description == 'Test Description')

    def test_Version_update(self):
        """
        Tests Version model update
        """
        model = VersionF.create(
            project=self.project,
        )
        new_model_data = {
            '10002001': u'10002001',
            'description': u'New description',
        }
        model.__dict__.update(new_model_data)
        model.save()

        # check if updated
        for key, val in new_model_data.items():
            self.assertEqual(model.__dict__.get(key), val)

    def test_formatted_release_date(self):
        """Tests we can get, set and present the release date nicely."""
        model = VersionF.create(
            description=u'New description',
            release_date=datetime(2016, 6, 6),
            project=self.project,
        )
        self.assertEqual(model.formatted_release_date(), '6 June, 2016')

    def test_Version_delete(self):
        """
        Tests Version model delete
        """
        model = VersionF.create(
            project=self.project,
        )

        model.delete()

        # check if deleted
        self.assertTrue(model.pk is None)


class TestVersionSponsors(TestCase):
    """
    Tests that we can filter sponsors for a version.
    """

    def setUp(self):
        """
        Sets up before each test
        """
        pass


class TestValidateEmailAddress(TestCase):
    """Test validate_email_address function."""

    def test_validation_failed_must_raise_ValidationError(self):
        from changes.models import validate_email_address
        email = 'email@wrongdomain'
        msg = f'{email} is not a valid email address'
        with self.assertRaisesMessage(ValidationError, msg):
            validate_email_address(email)
