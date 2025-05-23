# coding=utf-8
# flake8: noqa

import datetime
import json
from datetime import timedelta
from unittest import mock
from django.urls import reverse
from django.test import TestCase, override_settings
from django.test.client import Client
from base.tests.model_factories import ProjectF
from changes.tests.model_factories import (
    CategoryF,
    EntryF,
    VersionF)
from core.model_factories import UserF
import logging


class TestCategoryViews(TestCase):

    """Tests that Category views work."""

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test
        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s
        """
        self.client = Client()
        self.client.post(
                '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.category = CategoryF.create(project=self.project)
        self.user = UserF.create(**{
            'username': 'timlinux',
            'password': 'password',
            'is_staff': True
        })
        # Something changed in the way factoryboy works with django 1.8
        # I think - we need to explicitly set the users password
        # because the core.model_factories.UserF._prepare method
        # which sets the password is never called. Next two lines are
        # a work around for that - sett #581
        self.user.set_password('password')
        self.user.save()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.

        :return:
        """
        self.project.delete()
        self.category.delete()
        self.user.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryListView(self):

        response = self.client.get(reverse('category-list'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryCreateView_with_login(self):

        status = self.client.login(username='timlinux', password='password')
        self.assertTrue(status)
        url = reverse(
            'category-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/create.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryCreateView_no_login(self):

        response = self.client.get(reverse('category-create'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryCreate_with_login(self):

        self.client.login(username='timlinux', password='password')
        post_data = {
            'name': u'New Test Category',
            'project': self.project.id,
            'sort_number': 0
        }
        response = self.client.post(reverse('category-create'), post_data)
        self.assertRedirects(
            response,
            reverse(
                'category-list'))

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryCreate_no_login(self):

        post_data = {
            'name': u'New Test Category'
        }
        response = self.client.post(reverse('category-create'), post_data)
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryDetailView(self):

        response = self.client.get(reverse('category-detail', kwargs={
            'slug': self.category.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/detail.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryDeleteView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('category-delete', kwargs={
            'slug': self.category.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/delete.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryDeleteView_no_login(self):

        response = self.client.get(reverse('category-delete', kwargs={
            'slug': self.category.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryDelete_with_login(self):

        category_to_delete = CategoryF.create(project=self.project)
        self.client.login(username='timlinux', password='password')
        response = self.client.post(reverse('category-delete', kwargs={
            'slug': category_to_delete.slug
        }), {})
        self.assertRedirects(response, reverse('category-list'))
        # TODO: The following line to test that
        # the object is deleted does not currently pass as expected.
        # self.assertTrue(category_to_delete.pk is None)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryDelete_no_login(self):

        category_to_delete = CategoryF.create(
            project=self.project,
        )
        response = self.client.post(reverse('category-delete', kwargs={
            'slug': category_to_delete.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryOrederView_wiht_login_as_no_staff(self):
        self.user = UserF.create(**{
            'username': 'dimas',
            'password': 'password',
            'is_staff': False
        })
        self.client.login(
            username='dimas',
            password='password')
        response = self.client.get(reverse('category-order'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryOrderView_with_login_as_staff(self):
        self.client.login(
            username='timlinux',
            password='password')
        response = self.client.get(reverse('category-order'))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/order.html', u'changes/entry_list.html'
        ]
        self.assertTrue(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryOrderView_no_login(self):

        response = self.client.get(reverse('category-order'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryOrder_with_login(self):
        category_to_order = CategoryF.create(
            project=self.project,
            id=2,
            sort_number=1)
        self.client.login(username='timlinux', password='password')
        post_data = [{
            'name': u'New Test Category',
            'id': '2',
            'sort_number': '0'
        }]

        response = self.client.post(reverse('category-submit-order'), json.dumps(post_data), content_type='application/json')

        self.assertEqual(response.status_code, 200)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_CategoryOrder_with_no_login(self):
        category_to_order = CategoryF.create(
            project=self.project,
            id=2,
            sort_number=1)
        post_data = [{
            'name': u'New Test Category',
            'id': '2',
            'sort_number': '0'
        }]

        response = self.client.post(reverse('category-submit-order'), json.dumps(post_data), content_type='application/json')

        self.assertEqual(response.status_code, 302)


class TestEntryViews(TestCase):

    """Tests that Entry views work."""

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test

        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s
        """

        self.client = Client()
        self.client.post(
                '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(
                project=self.project,
                name='1.0.1')
        self.category = CategoryF.create(
                project=self.project,
                name='testcategory')
        self.entry = EntryF.create(
            category=self.category,
            version=self.version,
            title='testentry')
        self.pending_entry = EntryF.create(
            category=self.category,
            version=self.version,
            title='testentry2')
        self.user = UserF.create(**{
            'username': 'timlinux',
            'password': 'password',
            'is_staff': True
        })
        # Something changed in the way factoryboy works with django 1.8
        # I think - we need to explicitly set the users password
        # because the core.model_factories.UserF._prepare method
        # which sets the password is never called. Next two lines are
        # a work around for that - sett #581
        self.user.set_password('password')
        self.user.save()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.

        :return:
        """
        self.project.delete()
        self.version.delete()
        self.category.delete()
        self.entry.delete()
        self.user.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryCreateView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('entry-create', kwargs={
            'version_slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'entry/create.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryCreateView_no_login(self):

        response = self.client.get(reverse('entry-create', kwargs={
            'version_slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryCreate_with_login(self):

        self.client.login(username='timlinux', password='password')
        post_data = {
            'title': u'New Test Entry',
            'version': self.version.id,
            'category': self.category.id,
            'author': self.user.id
        }
        response = self.client.post(reverse('entry-create', kwargs={
            'version_slug': self.version.slug
        }), post_data)
        self.assertRedirects(
            response,
            reverse(
                'version-detail',
                kwargs={
                    'slug': self.version.slug}))

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryCreate_no_login(self):

        post_data = {
            'title': u'New Test Entry',
            'version': self.version.id,
            'category': self.category.id
        }
        response = self.client.post(reverse('entry-create', kwargs={
            'version_slug': self.version.slug
        }), post_data)
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryUpdateView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('entry-update', kwargs={
            'pk': self.entry.id
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'entry/update.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryUpdateView_no_login(self):

        response = self.client.get(reverse('entry-update', kwargs={
            'pk': self.entry.id
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryUpdate_with_login(self):

        self.client.login(username='timlinux', password='password')
        post_data = {
            'title': u'New Test Entry Updated',
            'version': self.version.id,
            'category': self.category.id,
            'author': self.user.id
        }
        response = self.client.post(reverse('entry-update', kwargs={
            'pk': self.entry.id
        }), post_data)
        self.assertRedirects(
            response,
            reverse(
                'version-detail',
                kwargs={
                    'slug': self.version.slug}))

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryUpdate_no_login(self):

        post_data = {
            'title': u'New Test Entry Updated',
            'version': self.version.id,
            'category': self.category.id
        }
        response = self.client.post(reverse('entry-update', kwargs={
            'pk': self.entry.id
        }), post_data)
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryDetailView(self):
        """Test the entry detail view."""
        url = reverse('entry-detail', kwargs={
            'pk': self.entry.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'entry/detail.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryDeleteView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('entry-delete', kwargs={
            'pk': self.entry.id
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'entry/delete.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryDeleteView_no_login(self):

        response = self.client.get(reverse('entry-delete', kwargs={
            'pk': self.entry.id
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryDelete_with_login(self):

        entry_to_delete = EntryF.create(
            category=self.category,
            version=self.version)
        self.client.login(username='timlinux', password='password')
        response = self.client.post(reverse('entry-delete', kwargs={
            'pk': entry_to_delete.id
        }), {})
        self.assertRedirects(response, reverse('version-detail', kwargs={
            'slug': self.version.slug
        }))
        # TODO: The following line to test that the object is deleted does not
        # currently pass as expected.
        # self.assertTrue(entry_to_delete.pk is None)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_EntryDelete_no_login(self):

        entry_to_delete = EntryF.create(
            category=self.category,
            version=self.version)
        response = self.client.post(reverse('entry-delete', kwargs={
            'pk': entry_to_delete.id
        }))
        self.assertEqual(response.status_code, 302)


def mocked_convert(*args, **kwargs):
    return 'Mock document'


class TestVersionViews(TestCase):

    """Tests that Version views work."""

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test
        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s
        """

        self.client = Client()
        self.client.post(
                '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(
                project=self.project,
                name='1.0.1')
        self.category = CategoryF.create(
                project=self.project,
                name='testcategory')

        self.user = UserF.create(**{
            'username': 'timlinux',
            'password': 'password',
            'is_staff': True
        })
        # Something changed in the way factoryboy works with django 1.8
        # I think - we need to explicitly set the users password
        # because the core.model_factories.UserF._prepare method
        # which sets the password is never called. Next two lines are
        # a work around for that - sett #581
        self.user.set_password('password')
        self.user.save()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.

        :return:
        """
        self.project.delete()
        self.version.delete()
        self.category.delete()
        self.user.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionListView(self):

        response = self.client.get(reverse('version-list'))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'version/list.html', u'changes/version_list.html'
        ]
        self.assertEqual(response.template_name, expected_templates)
        self.assertEqual(response.context_data['object_list'][0],
                         self.version)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreateView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('version-create'))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'version/create.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreateView_no_login(self):

        response = self.client.get(reverse('version-create'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreate_with_login(self):

        self.client.login(username='timlinux', password='password')
        post_data = {
            'project': self.project.id,
            'name': u'1.8.1',
            'description': u'This is a test description',
            'author': self.user.id
        }
        response = self.client.post(reverse('version-create'), post_data)
        self.assertRedirects(
            response, reverse('version-list')
        )

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreate_no_login(self):

        post_data = {
            'project': self.project.id,
            'name': u'New Test Version',
            'description': u'This is a test description'
        }
        response = self.client.post(reverse('version-create'), post_data)
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdateView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('version-update', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'version/update.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdateView_no_login(self):

        response = self.client.get(reverse('version-update', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdate_with_login(self):

        self.client.login(username='timlinux', password='password')
        post_data = {
            'project': self.project.id,
            'name': u'1.5.1',
            'description': u'This is a test description',
            'author': self.user.id
        }
        response = self.client.post(reverse('version-update', kwargs={
            'slug': self.version.slug
        }), post_data)
        self.assertRedirects(response, reverse('version-list'))

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdate_no_login(self):

        post_data = {
            'project': self.project.id,
            'name': u'New Test Version',
            'description': u'This is a test description'
        }
        response = self.client.post(reverse('version-update', kwargs={
            'slug': self.version.slug
        }), post_data)
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDetailView(self):

        response = self.client.get(reverse('version-detail', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'version/detail.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDeleteView_with_login(self):

        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('version-delete', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'version/delete.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDeleteView_no_login(self):

        response = self.client.get(reverse('version-delete', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDelete_with_login(self):

        version_to_delete = VersionF.create(
                project=self.project,
                name='8.1.1')
        post_data = {
            'pk': version_to_delete.pk
        }
        self.client.login(username='timlinux', password='password')
        response = self.client.post(reverse('version-delete', kwargs={
            'slug': version_to_delete.slug
        }), post_data)
        self.assertRedirects(response, reverse('version-list'))
        # TODO: The following line to test that the object is deleted does
        # not currently pass as expected.
        # self.assertTrue(version_to_delete.pk is None)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDelete_no_login(self):

        version_to_delete = VersionF.create(
                project=self.project,
                name='2.0.1')
        response = self.client.post(reverse('version-delete', kwargs={
            'slug': version_to_delete.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDownload_no_login(self):
        other_project = ProjectF.create()
        version_same_name_from_other_project = VersionF.create(
            project=other_project,
            name='1.0.2'
        )
        response = self.client.get(reverse('version-download', kwargs={
            'slug': version_same_name_from_other_project.slug
        }))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver', ])
    @mock.patch('pypandoc.convert_text', side_effect=mocked_convert)
    def test_VersionDownload_login(self, mocked_convert):
        self.client.login(username='timlinux', password='password')
        other_project = ProjectF.create()
        version_same_name_from_other_project = VersionF.create(
            project=other_project,
            name='1.0.3'
        )
        response = self.client.get(reverse('version-download', kwargs={
            'slug': version_same_name_from_other_project.slug
        }))
        self.assertEqual(
            response.context.get('version'),
            version_same_name_from_other_project)
        self.assertEqual(response.status_code, 200)

    @override_settings(VALID_DOMAIN=['testserver', ])
    @mock.patch('pypandoc.convert_text', side_effect=mocked_convert)
    def test_VersionDownloadMd(self, mocked_convert):
        other_project = ProjectF.create()
        version_same_name_from_other_project = VersionF.create(
            project=other_project,
            name='1.0.4'
        )
        response = self.client.get(reverse('version-download-md', kwargs={
            'slug': version_same_name_from_other_project.slug
        }))
        self.assertEqual(
            response.context.get('version'),
            version_same_name_from_other_project)
        self.assertEqual(response.status_code, 200)

    @override_settings(VALID_DOMAIN=['testserver', ])
    @mock.patch('pypandoc.convert_text', side_effect=mocked_convert)
    def test_VersionDownload_login_notfound(self, mocked_convert):
        self.client.login(username='timlinux', password='password')
        response = self.client.get(reverse('version-download', kwargs={
            'slug': 'not-found'
        }))
        self.assertEqual(response.status_code, 404)
        response = self.client.get(reverse('version-download', kwargs={
            'slug': 'not-found'
        }))
        self.assertEqual(response.status_code, 404)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_download_all_referenced_images(self):
        self.client.login(username='timlinux', password='password')
        response = self.client.get(
            reverse('download-referenced-images', kwargs={
                'slug': self.version.slug
            }))
        self.assertEqual(response.status_code, 200)


class TestVersionViewsWithAnonymousUserForCRUD(TestCase):
    """
    Check if anonymous user can perform CRUD operations on version entries
    just in case they have the URL to the views.
    """

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test.
        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s.
        """

        self.client = Client()
        self.client.post(
            '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(
            project=self.project,
            name='1.0.1')
        self.category = CategoryF.create(
            project=self.project,
            name='testcategory')

        self.user = None

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.
        """
        self.project.delete()
        self.version.delete()
        self.category.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionListView_with_anonymous_user(self):
        """
        Test if anonymous user can view version entry list.
        """
        response = self.client.get(reverse('version-list'))

        expected_templates = [
            'version/list.html', u'changes/version_list.html'
        ]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, expected_templates)
        self.assertEqual(response.context_data['object_list'][0],
                         self.version)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreateView_with_anonymous_user(self):
        """
        Test if anonymous user can create a version entry.
        """
        response = self.client.get(reverse('version-create'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver'])
    def test_VersionUpdateView_with_anonymous_user(self):
        """
        Test if anonymous user can update a version entry.
        """
        response = self.client.get(reverse('version-create'))
        self.assertEqual(response.status_code, 302)

    @override_settings(VALID_DOMAIN=['testserver'])
    def test_VersionDeleteView_with_anonymous_user(self):
        """
        Test if anonymous user can delete a version entry.
        """
        response = self.client.get(reverse('version-delete', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 302)


class TestVersionViewsWithNormalUserForCRUD(TestCase):
    """
    Check if normal(a regular logged in user) user can perform CRUD.
    """

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test.
        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s.
        """

        self.client = Client()
        self.client.post(
            '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(
            project=self.project,
            name='1.0.1')
        self.category = CategoryF.create(
            project=self.project,
            name='testcategory')

        # Here we create a normal User without staff permissions.
        self.user = UserF.create(**{
            'username': 'sonlinux',
            'password': 'password',
            'is_staff': False
        })

        # Something changed in the way factoryboy works with django 1.8
        # I think - we need to explicitly set the users password
        # because the core.model_factories.UserF._prepare method
        # which sets the password is never called. Next two lines are
        # a work around for that - sett #581
        self.user.set_password('password')
        self.user.save()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.
        """
        self.project.delete()
        self.version.delete()
        self.category.delete()
        self.user.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionListView_with_normal_user(self):
        """
        Test if a normal user can view a list of version entries.
        """
        self.client.login(username='sonlinux', password='password')
        response = self.client.get(reverse('version-list'))

        expected_templates = [
            'version/list.html', u'changes/version_list.html'
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, expected_templates)
        self.assertEqual(response.context_data['object_list'][0],
                         self.version)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreateView_with_normal_user(self):
        """
        Test if a normal user can create a list of version entries.
        """
        self.client.login(username='sonlinux', password='password')
        response = self.client.get(reverse('version-create'))

        self.assertEqual(response.status_code, 200)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdateView_with_normal_user(self):
        """
        Test if normal user can update a version entry.
        """
        self.client.login(username='sonlinux', password='password')

        # lets ensure the user updating owns the project.
        response = self.client.get(reverse('category-delete', kwargs={
            'slug': self.category.slug
        }))

        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/delete.html'
        ]

        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDeleteView_with_normal_user(self):
        """
        Test if a normal user can delete a version entry.
        """
        self.client.login(username='sonlinux', password='password')

        response = self.client.get(reverse('category-delete', kwargs={
            'slug': self.category.slug
        }))

        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/delete.html'
        ]

        self.assertEqual(response.template_name, expected_templates)


class TestVersionViewsWithStaffUserForCRUD(TestCase):
    """
    Test if staff user can perform CRUD operations on a version entry.
    """

    @override_settings(VALID_DOMAIN=['testserver', ])
    def setUp(self):
        """
        Setup before each test.
        We force the locale to en otherwise it will use
        the locale of the host running the tests and we
        will get unpredictable results / 404s.
        """

        self.client = Client()
        self.client.post(
            '/set_language/', data={'language': 'en'})
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(
            project=self.project,
            name='1.0.1')
        self.category = CategoryF.create(
            project=self.project,
            name='testcategory')

        self.user = UserF.create(**{
            'username': 'sonlinux',
            'password': 'password',
            'is_staff': True
        })

        # Something changed in the way factoryboy works with django 1.8
        # I think - we need to explicitly set the users password
        # because the core.model_factories.UserF._prepare method
        # which sets the password is never called. Next two lines are
        # a work around for that - sett #581
        self.user.set_password('password')
        self.user.save()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def tearDown(self):
        """
        Teardown after each test.
        """
        self.project.delete()
        self.version.delete()
        self.category.delete()
        self.user.delete()

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionListView_with_staff_user(self):
        """
        Test if staff user can view a list of version entries.
        """
        response = self.client.get(reverse('version-list'))
        self.assertEqual(response.status_code, 200)

        expected_template = [
            'version/list.html', u'changes/version_list.html'
        ]

        self.assertEqual(response.template_name, expected_template)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionCreateView_with_staff_user(self):
        """
        Test if staff user can create a version entry.
        """
        self.client.login(username='sonlinux', password='password')

        post_data = {
            'project': self.project.id,
            'name': u'2.0.3',
            'description': u'Test create with staff user',
            'author': self.user.id
        }

        response = self.client.get(reverse('version-create'), post_data)

        self.assertEqual(response.status_code, 200)

        expected_template = [
            'version/create.html'
        ]
        self.assertEqual(response.template_name, expected_template)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionUpdateView_with_staff_user(self):
        """
        Test if staff user can update a version entry.
        """
        self.client.login(username='sonlinux', password='password')

        response = self.client.get(reverse('version-update', kwargs={
            'slug': self.version.slug
        }))
        self.assertEqual(response.status_code, 200)

        expected_templates = [
            'version/update.html'
        ]
        self.assertEqual(response.template_name, expected_templates)

    @override_settings(VALID_DOMAIN=['testserver', ])
    def test_VersionDeleteView_with_staff_user(self):
        """
        Test if staff user can delete a version entry.
        """
        self.client.login(username='sonlinux', password='password')

        response = self.client.get(reverse('category-delete', kwargs={
            'slug': self.category.slug
        }))

        self.assertEqual(response.status_code, 200)
        expected_templates = [
            'category/delete.html'
        ]

        self.assertEqual(response.template_name, expected_templates)