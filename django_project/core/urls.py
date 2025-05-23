# coding=utf-8
"""Project level url handler."""
from django.conf.urls import include
from django.urls import re_path as url
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views  # noqa
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseServerError
from django.template import loader
from .views import general_flatpage, index_view
from django.urls import path
from .views import UserAutocomplete, GetUserByPk
import traceback

admin.autodiscover()
handler404 = 'base.views.error_views.custom_404'


def handler500(request):
    """500 error handler which includes ``request`` in the context.

    See http://raven.readthedocs.org/en/latest/integrations/
        django.html#message-references

    :param request: Django request object.

    Templates: `500.html`
    Context: None
    """
    # You need to create a 500.html template.
    t = loader.get_template('500.html')
    error_traceback = traceback.format_exc()
    print(error_traceback)  # Print the error traceback for debugging
    return HttpResponseServerError(t.render({
        'request': request,
        'user': request.user,  # Add the user to the context
    }))


urlpatterns = [
    # force redirect to /en/
    # to fix 500 error temporarily  after user logged in on production
    url(r'^$', index_view),
]
# These patterns work if there is a locale code injected in front of them
# e.g. /en/reports/
urlpatterns += i18n_patterns(
    url(r'^site-admin/', admin.site.urls),
    url(r'^', include('base.urls')),
    url(r'^', include('changes.urls')),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^stripe/', include("djstripe.urls", namespace="djstripe")),
    url(r'^notifications/', include('pinax.notifications.urls',
                                    namespace='pinax_notifications')),
    url(r'^flatpage/(?P<url>.*)$',
        general_flatpage,
        name='general_flatpage'),
)
urlpatterns += [
    url(r'^tinymce/', include('tinymce.urls')),
]

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^rosetta/', include('rosetta.urls')),
    ]

urlpatterns += [
    path("autocomplete/users/", UserAutocomplete.as_view(), name="user-autocomplete"),
    path("get_user_by_pk/<int:pk>/", GetUserByPk.as_view(), name="get-user-by-pk"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
