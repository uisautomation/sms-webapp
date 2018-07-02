"""
Views

"""
import logging

import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

LOG = logging.getLogger(__name__)

# Default session used for making HTTP requests.
DEFAULT_REQUESTS_SESSION = requests.Session()


def media(request, media_key):
    """
    :param request: the current request
    :param media_key: JW media key of the required media

    This method handles a request to render an individual media page

    """
    response = DEFAULT_REQUESTS_SESSION.get(settings.MEDIA_API_URL + '/media/' + media_key)

    if not response.ok:
        return HttpResponse(status=response.status_code)

    return render(request, 'ui/media.html', {
        'media_item': response.json(),
        'media_item_json': response.content.decode("utf-8")
    })
