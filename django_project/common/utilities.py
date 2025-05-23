# coding=utf-8
"""**Utilities functions**
"""

__author__ = 'Ismail Sunni <ismail@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '23/04/2014'
__license__ = ''
__copyright__ = ''


from slugify import Slugify
from django.http import Http404, HttpResponse
import json


version_slugify = Slugify()
version_slugify.safe_chars = '.'


def re_order_features(request, features):
    """Helper to reorder a set of features.

    The column must be called `sequence_number` in your model.

    :param request: HTTP request object.
    :type request: HttpRequest

    :param features: A queryset of features to update.
    :type features: QuerySet

    :return: An empty HTTP 200 response.
    :rtype: HttpResponse
    :raises: Http404
    """
    try:
        sequence_order_request = json.loads(request.body)
    except ValueError:
        raise Http404('Error JSON values')

    # Add dummy shift in the DB to avoid Integrity about unique_together
    for feature in features:
        feature.sequence_number += len(sequence_order_request)
        feature.save()

    for order_request in sequence_order_request:
        feature = features.get(id=order_request['id'])
        if feature:
            feature.sequence_number = order_request['sort_number']
            feature.save()

    return HttpResponse('')
