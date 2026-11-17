# coding=utf-8
from django import forms
from django.forms.widgets import TextInput
from django.core.validators import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Field,
    HTML,
    Div,
)
from .models import (
    Category,
    Version,
    Entry,
)
from crispy_bulma.widgets import FileUploadInput

FileUploadInput.template_name = 'widgets/file_upload_input.html'

ENTRY_FORM_TABS = (
    '<div class="tabs is-boxed is-hidden" data-entry-tabs>'
    '<ul class="ml-0 mt-0" role="tablist" aria-label="Entry form">'
    '<li>'
    '<a class="is-active" role="tab" id="entry-tab-write"'
    ' aria-controls="entry-write-panel" aria-selected="true" tabindex="0">'
    '<span class="icon is-small">'
    '<i class="fas fa-pen" aria-hidden="true"></i>'
    '</span>'
    '<span>Write</span>'
    '</a>'
    '</li>'
    '<li>'
    '<a role="tab" id="entry-tab-preview"'
    ' aria-controls="entry-preview-panel" aria-selected="false"'
    ' tabindex="-1">'
    '<span class="icon is-small">'
    '<i class="fas fa-eye" aria-hidden="true"></i>'
    '</span>'
    '<span>Preview</span>'
    '</a>'
    '</li>'
    '</ul>'
    '</div>'
)

ENTRY_PREVIEW_PANEL = (
    '<div id="entry-preview-panel" class="is-hidden"></div>'
)


class CategoryForm(forms.ModelForm):
    # noinspection PyClassicStyleClass
    class Meta:
        model = Category
        fields = ('name', 'sort_number')

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'New Category in {self.project.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Category {kwargs["instance"].name}'
                '</h2>'
            )
        layout = Layout(
            Fieldset(
                form_title,
                Field('name', css_class='form-control'),
                Field('sort_number', css_class='form-control'),
                css_id='project-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        instance.project = self.project
        instance.save()
        return instance

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            if 'name' in cleaned_data:
                Category.objects.get(
                    name=cleaned_data['name'], project=self.project)
        except Category.DoesNotExist:
            pass
        else:
            raise ValidationError(
                'Category with this name already exists for this project'
            )

        return cleaned_data


class VersionForm(forms.ModelForm):
    image_file = forms.ImageField(widget=FileUploadInput, required=False)
    # noinspection PyClassicStyleClass

    class Meta:
        model = Version
        fields = (
            'name',
            'description',
            'image_file',
            'release_date'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'New Version in {self.project.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Version {kwargs["instance"].name}'
                '</h2>'
            )
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                Field('name'),
                Field('description'),
                Field('image_file'),
                Field('release_date'),
                css_id='project-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(VersionForm, self).__init__(*args, **kwargs)
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )

    def save(self, commit=True):
        instance = super(VersionForm, self).save(commit=False)
        instance.author = self.user
        instance.project = self.project
        instance.approved = False
        instance.save()
        return instance


class EntryForm(forms.ModelForm):

    # noinspection PyClassicStyleClass
    image_file = forms.ImageField(widget=FileUploadInput, required=False)

    class Meta:
        model = Entry
        fields = (
            'category', 'title', 'description',
            'image_file', 'image_credits', 'video',
            'funded_by', 'funder_url', 'developed_by',
            'developer_url', 'github_PR_url'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.version = kwargs.pop('version')
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'New Entry in {self.project.name} {self.version.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Entry {kwargs["instance"].title}'
                '</h2>'
            )
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                HTML(ENTRY_FORM_TABS),
                Div(
                    Field('category', css_class='form-control'),
                    Field('title', css_class='form-control'),
                    Field('description', css_class='form-control'),
                    Field('image_file', css_class='form-control'),
                    Field('image_credits', css_class='form-control'),
                    Field('video', css_class='form-control'),
                    Field('funded_by', css_class='form-control'),
                    Field('funder_url', css_class='form-control'),
                    Field('developed_by', css_class='form-control'),
                    Field('developer_url', css_class='form-control'),
                    Field('github_PR_url', css_class='form-control'),
                    css_id='entry-write-panel'),
                HTML(ENTRY_PREVIEW_PANEL),
                css_id='entry-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(EntryForm, self).__init__(*args, **kwargs)
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )
        self.fields['title'].label = 'Feature Title'
        # Need to add required=False explicitly for these because
        # even though they are declared as not required in the model,
        # crispy is rendering them as required.
        self.fields['video'].label = 'Video URL'
        self.fields['video'] = forms.URLField(
                widget=TextInput, required=False)
        self.fields['funder_url'].label = 'Funder URL'
        self.fields['funder_url'] = forms.URLField(
                widget=TextInput, required=False)
        self.fields['developer_url'] = forms.URLField(
                widget=TextInput, required=False)
        self.fields['developer_url'].label = 'Developer URL'
        # Filter the category list when editing so it shows only relevant ones
        self.fields['category'].queryset = Category.objects.filter(
            project=self.project).order_by('name')

    def save(self, commit=True):
        instance = super(EntryForm, self).save(commit=False)
        instance.author = self.user
        instance.version = self.version
        instance.approved = False
        instance.save()
        return instance
