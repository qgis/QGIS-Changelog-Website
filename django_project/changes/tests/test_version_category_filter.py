# coding=utf-8
"""Tests for the category list and filter on the version page."""

import logging

from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from base.tests.model_factories import ProjectF
from changes.models import Version
from changes.tests.model_factories import CategoryF, EntryF, VersionF


@override_settings(VALID_DOMAIN=['testserver', ])
class TestVersionCategorySidebar(TestCase):
    """The sidebar lists a version's categories on its detail page."""

    def setUp(self) -> None:
        self.client = Client()
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        version = VersionF.create(project=self.project, name='4.4')
        Version.objects.filter(pk=version.pk).update(slug='bratislava')
        self.version = Version.objects.get(pk=version.pk)
        self.map_tools = CategoryF.create(
            project=self.project, name='Map tools')
        EntryF.create(version=self.version, category=self.map_tools)

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)

    def test_sidebar_lists_categories_when_name_and_slug_differ(self) -> None:
        response = self.client.get(
            reverse('version-detail', kwargs={'slug': 'bratislava'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="categories"')
