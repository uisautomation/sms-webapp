"""
Views

"""
import logging

import requests
from django.conf import settings
from django.shortcuts import render

LOG = logging.getLogger(__name__)

# Default session used for making HTTP requests.
DEFAULT_REQUESTS_SESSION = requests.Session()


def media(request, media_key):
    """
    :param request: the current request
    :param media_key: JW media key of the required media

    FIXME

    """
    response = DEFAULT_REQUESTS_SESSION.get(settings.MEDIA_API_URL + 'media/' + media_key)

    # Check that the call to the Media API succeeded.
    response.raise_for_status()

    return render(request, 'ui/media.html', {'media_item': response.content.decode("utf-8")})
