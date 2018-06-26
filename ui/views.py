"""
Views

"""
import logging

from django.shortcuts import render

LOG = logging.getLogger(__name__)


def media(request, media_key):
    """
    :param request: the current request
    :param media_key: JW media key of the required media

    FIXME

    """
    return render(request, 'ui/media.html', {'media_key': media_key})
