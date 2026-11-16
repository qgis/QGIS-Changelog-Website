# coding=utf-8
"""Tests for the Write and Preview tabs on the entry form."""

import logging

from crispy_forms.layout import HTML, Div
from django.test import TestCase, override_settings
from django.test.client import Client
from django.urls import reverse

from base.tests.model_factories import ProjectF
from changes.forms import ENTRY_FORM_TABS, ENTRY_PREVIEW_PANEL, EntryForm
from changes.models import Entry
from changes.tests.model_factories import CategoryF, EntryF, VersionF
from core.model_factories import UserF


class EntryFormTestCase(TestCase):
    """A version with one entry, and a staff user who can edit it."""

    def setUp(self) -> None:
        self.client = Client()
        logging.disable(logging.CRITICAL)
        self.project = ProjectF.create()
        self.version = VersionF.create(project=self.project, name='4.4')
        self.category = CategoryF.create(project=self.project)
        self.entry = EntryF.create(
            version=self.version,
            category=self.category,
            title='Snapping to curves',
            description='Snapping now works on curved segments.')
        self.user = UserF.create(username='editor', is_staff=True)
        self.user.set_password('password')
        self.user.save()

    def tearDown(self) -> None:
        logging.disable(logging.NOTSET)

    def create_url(self) -> str:
        return reverse(
            'entry-create', kwargs={'version_slug': self.version.slug})

    def update_url(self) -> str:
        return reverse('entry-update', kwargs={'pk': self.entry.pk})


@override_settings(VALID_DOMAIN=['testserver', ])
class TestEntryFormTabs(EntryFormTestCase):
    """The whole entry form sits under the Write and Preview tabs."""

    def test_tabs_wrap_every_field(self) -> None:
        form = EntryForm(
            user=self.user, version=self.version, project=self.project)
        tabs, write_panel, preview_panel = form.helper.layout[0].fields
        self.assertIsInstance(tabs, HTML)
        self.assertEqual(tabs.html, ENTRY_FORM_TABS)
        self.assertIsInstance(write_panel, Div)
        self.assertEqual(write_panel.css_id, 'entry-write-panel')
        self.assertEqual(
            [field.fields[0] for field in write_panel.fields],
            list(EntryForm.Meta.fields))
        self.assertIsInstance(preview_panel, HTML)
        self.assertEqual(preview_panel.html, ENTRY_PREVIEW_PANEL)

    def test_tabs_markup(self) -> None:
        self.assertIn('tabs is-boxed', ENTRY_FORM_TABS)
        self.assertIn('role="tablist"', ENTRY_FORM_TABS)
        self.assertIn('aria-controls="entry-write-panel"', ENTRY_FORM_TABS)
        self.assertIn('aria-controls="entry-preview-panel"', ENTRY_FORM_TABS)
        self.assertIn('is-hidden', ENTRY_FORM_TABS)
        self.assertIn('is-hidden', ENTRY_PREVIEW_PANEL)

    def assert_page_has_tabs(self, url: str) -> None:
        self.client.login(username='editor', password='password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-entry-tabs', count=1)
        self.assertContains(response, 'id="entry-write-panel"', count=1)
        self.assertContains(response, 'id="entry-preview-panel"', count=1)

    def test_create_page_shows_tabs(self) -> None:
        self.assert_page_has_tabs(self.create_url())

    def test_update_page_shows_tabs(self) -> None:
        self.assert_page_has_tabs(self.update_url())


@override_settings(VALID_DOMAIN=['testserver', ])
class TestEntryPreview(EntryFormTestCase):
    """The Preview tab renders the posted entry and saves nothing."""

    def preview_data(self, **overrides: str) -> dict[str, str]:
        data = {
            'category': str(self.category.pk),
            'title': 'Raster stretch preview',
            'description': 'The **stretch** updates as you drag.',
            'preview': '1',
        }
        data.update(overrides)
        return data

    def test_create_preview_renders_the_entry_without_saving(self) -> None:
        self.client.login(username='editor', password='password')
        entry_count = Entry.objects.count()
        response = self.client.post(self.create_url(), self.preview_data())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'entry/includes/entry_detail.html')
        self.assertTemplateNotUsed(response, 'entry/create.html')
        self.assertContains(response, 'Raster stretch preview')
        self.assertContains(response, '<strong>stretch</strong>')
        self.assertEqual(Entry.objects.count(), entry_count)

    def test_update_preview_leaves_the_entry_unchanged(self) -> None:
        self.client.login(username='editor', password='password')
        response = self.client.post(self.update_url(), self.preview_data())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Raster stretch preview')
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, 'Snapping to curves')

    def test_preview_hides_the_entry_buttons(self) -> None:
        self.client.login(username='editor', password='password')
        response = self.client.post(self.update_url(), self.preview_data())
        self.assertNotContains(response, 'Update Entry')
        self.assertNotContains(response, 'Delete Entry')
        self.assertNotContains(response, 'Get Permalink')

    def test_preview_renders_an_incomplete_form(self) -> None:
        self.client.login(username='editor', password='password')
        entry_count = Entry.objects.count()
        response = self.client.post(
            self.create_url(), self.preview_data(title='', category=''))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'entry/includes/entry_detail.html')
        self.assertContains(response, '<strong>stretch</strong>')
        self.assertEqual(Entry.objects.count(), entry_count)

    def test_preview_shows_a_picked_gif_as_animation(self) -> None:
        self.client.login(username='editor', password='password')
        response = self.client.post(
            self.create_url(), self.preview_data(preview_image='drag.gif'))
        self.assertContains(response, 'entry-preview-image.gif')
        self.assertContains(response, 'data-gifffer=')

    def test_preview_shows_a_picked_picture(self) -> None:
        self.client.login(username='editor', password='password')
        response = self.client.post(
            self.create_url(), self.preview_data(preview_image='stretch.png'))
        self.assertContains(response, 'entry-preview-image')
        self.assertContains(response, 'pop-image')
        self.assertNotContains(response, 'data-gifffer=')

    def test_preview_needs_a_login(self) -> None:
        response = self.client.post(self.create_url(), self.preview_data())
        self.assertEqual(response.status_code, 302)
        self.assertNotContains(
            response, 'Raster stretch preview', status_code=302)

    def test_preview_respects_a_locked_version(self) -> None:
        self.version.locked = True
        self.version.save()
        self.client.login(username='editor', password='password')
        response = self.client.post(self.update_url(), self.preview_data())
        self.assertEqual(response.status_code, 404)
