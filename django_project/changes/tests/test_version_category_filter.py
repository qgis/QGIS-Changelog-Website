# coding=utf-8
"""Tests for the category list and filter on the version page."""

import logging

from django.http import HttpResponse
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse
from django.utils import translation

from base.tests.model_factories import ProjectF
from changes.models import Version
from changes.tests.model_factories import CategoryF, EntryF, VersionF


@override_settings(VALID_DOMAIN=['testserver', ])
class TestVersionCategorySidebar(TestCase):
    """The sidebar lists, counts and filters a version's categories."""

    def setUp(self) -> None:
        # With no active language, reverse() builds /en-us/ URLs that 404.
        translation.activate('en')
        self.client = Client()
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        version = VersionF.create(project=self.project, name='4.4')
        Version.objects.filter(pk=version.pk).update(slug='bratislava')
        self.version = Version.objects.get(pk=version.pk)
        self.map_tools = CategoryF.create(
            project=self.project, name='Map tools')
        self.symbology = CategoryF.create(
            project=self.project, name='Symbology')
        EntryF.create(
            version=self.version, category=self.map_tools,
            title='Snapping to curves')
        EntryF.create(
            version=self.version, category=self.map_tools,
            title='Ellipsoidal measure tool')
        EntryF.create(
            version=self.version, category=self.symbology,
            title='Raster stretch preview')

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)
        translation.deactivate()

    def get_detail(self, query: str = '') -> HttpResponse:
        url = reverse('version-detail', kwargs={'slug': 'bratislava'})
        return self.client.get(url + query)

    def test_sidebar_lists_categories_when_name_and_slug_differ(self) -> None:
        response = self.get_detail()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="categories"')

    def test_sidebar_shows_entry_count_per_category(self) -> None:
        response = self.get_detail()
        counts = {
            row['category'].name: len(row['entries'])
            for row in response.context['category_rows']}
        self.assertEqual(counts, {'Map tools': 2, 'Symbology': 1})
        self.assertEqual(response.context['entry_total'], 3)
        self.assertContains(response, '<span class="tag">2</span>')
        self.assertContains(response, '<span class="tag">3</span>')

    def test_sidebar_links_filter_by_category_slug(self) -> None:
        response = self.get_detail()
        self.assertContains(
            response, '?category=%s' % self.symbology.slug)

    def test_category_query_shows_only_that_category(self) -> None:
        response = self.get_detail('?category=%s' % self.symbology.slug)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['selected_category'], self.symbology)
        self.assertContains(response, 'Raster stretch preview')
        self.assertNotContains(response, 'Snapping to curves')
        self.assertNotContains(response, 'Ellipsoidal measure tool')
        self.assertContains(response, '<h1>Entries in Symbology</h1>')
        self.assertContains(response, 'aria-current="page"', count=1)

    def test_unknown_category_shows_every_entry(self) -> None:
        response = self.get_detail('?category=no-such-category')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['selected_category'])
        self.assertContains(response, 'Raster stretch preview')
        self.assertContains(response, 'Snapping to curves')
        self.assertContains(response, '<h1>Entries (all)</h1>')
