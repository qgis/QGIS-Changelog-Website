# coding=utf-8
from django import forms
from django.forms.widgets import TextInput
from django.core.validators import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Fieldset,
    Submit,
    Field,
    HTML,
)
from .models import (
    Category,
    Version,
    Entry,
    Sponsor,
    SponsorshipPeriod,
    SponsorshipLevel
)
from changes.utils.svgimagefile import SVGAndImageFormField
from crispy_bulma.widgets import FileUploadInput

FileUploadInput.template_name = 'widgets/file_upload_input.html'

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
    image_file = forms.ImageField(widget=FileUploadInput)
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
        try:
            version = Version.objects.get(pk=instance.pk)
        except Version.DoesNotExist:
            version = None
        if version and version.release_date:
            instance.release_date = version.release_date
        instance.author = self.user
        instance.project = self.project
        instance.approved = False
        instance.save()
        return instance


class EntryForm(forms.ModelForm):

    # noinspection PyClassicStyleClass
    image_file = forms.ImageField(widget=FileUploadInput)
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


class SponsorForm(forms.ModelForm):

    # noinspection PyClassicStyleClass
    class Meta:
        model = Sponsor
        fields = (
            'name',
            'contact_title',
            'address',
            'country',
            'sponsor_url',
            'contact_person',
            'sponsor_email',
            'agreement',
            'logo',
            'invoice_number',
            'project',
        )
        field_classes = {
            'logo': SVGAndImageFormField
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'New Sponsor for {self.project.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Sponsor {kwargs["instance"].name}'
                '</h2>'
            )
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                Field('name', css_class='form-control'),
                Field('contact_title', css_class='form-control'),
                Field('address', css_class='form-control'),
                Field('country', css_class='form-control chosen-select'),
                Field('sponsor_url', css_class='form-control'),
                Field('contact_person', css_class='form-control'),
                Field('sponsor_email', css_class='form-control'),
                Field('agreement', css_class='form-control'),
                Field('logo', css_class='form-control'),
                Field('invoice_number', css_class='form-control'),
                css_id='project-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(SponsorForm, self).__init__(*args, **kwargs)
        self.fields['project'].initial = self.project
        self.fields['project'].widget = forms.HiddenInput()
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )

    def save(self, commit=True):
        instance = super(SponsorForm, self).save(commit=False)
        instance.author = self.user
        instance.approved = False
        instance.save()
        return instance


class SponsorshipLevelForm(forms.ModelForm):

    logo = forms.ImageField(widget=FileUploadInput)
    # noinspection PyClassicStyleClass
    class Meta:
        model = SponsorshipLevel
        fields = (
            'name',
            'value',
            'currency',
            'logo'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'Sponsorship Level Form for {self.project.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Sponsorship Level {kwargs["instance"].name}'
                '</h2>'
            )
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                Field('name', css_class='form-control'),
                Field('value', css_class='form-control'),
                Field('currency', css_class='form-control'),
                Field('logo', css_class='form-control'),
                css_id='project-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(SponsorshipLevelForm, self).__init__(*args, **kwargs)
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )

    def save(self, commit=True):
        instance = super(SponsorshipLevelForm, self).save(commit=False)
        instance.author = self.user
        instance.project = self.project
        instance.save()
        return instance


class SponsorshipPeriodForm(forms.ModelForm):

    # noinspection PyClassicStyleClass
    class Meta:
        model = SponsorshipPeriod
        fields = (
            'sponsor',
            'sponsorship_level',
            'start_date',
            'end_date',
            'amount_sponsored',
            'currency'
        )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.project = kwargs.pop('project')
        form_title = (
            '<h2 class="is-title is-size-4">'
            f'Sponsorship Period Form for {self.project.name}'
            '</h2>'
        )
        if 'instance' in kwargs and kwargs['instance']:
            form_title = (
                '<h2 class="is-title is-size-4">'
                f'Edit Sponsorship Period {kwargs["instance"].name}'
                '</h2>'
            )
        self.helper = FormHelper()
        layout = Layout(
            Fieldset(
                form_title,
                Field('sponsor', css_class='form-control chosen-select'),
                Field(
                    'sponsorship_level',
                    css_class='form-control chosen-select'),
                Field('start_date', css_class='form-control'),
                Field('end_date', css_class='form-control'),
                Field('amount_sponsored', css_class='form-control'),
                Field('currency', css_class='form-control'),
                css_id='project-form')
        )
        self.helper.layout = layout
        self.helper.html5_required = False
        self.helper.form_class = 'box-content'
        super(SponsorshipPeriodForm, self).__init__(*args, **kwargs)
        # Filter items to only show the approved items in the same project
        self.fields['sponsor'].queryset = \
            Sponsor.objects.filter(
                project=self.project, approved=True).order_by('name')
        self.fields['sponsorship_level'].queryset = \
            SponsorshipLevel.objects.filter(
                project=self.project, approved=True).order_by('name')
        self.helper.layout.append(
            HTML(
                '<button type="submit" class="button is-success mt-5" name="submit">'
                '  <span class="icon"><i class="fas fa-check"></i></span>'
                '  <span>Submit</span>'
                '</button>'
            )
        )

    def save(self, commit=True):
        instance = super(SponsorshipPeriodForm, self).save(commit=False)
        instance.author = self.user
        instance.project = self.project
        instance.save()
        return instance


class SustainingMemberPeriodForm(forms.ModelForm):
    # noinspection PyClassicStyleClass
    class Meta:
        model = SponsorshipPeriod
        fields = (
            'sponsorship_level',
        )
