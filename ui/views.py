"""
Views

"""
import copy
import json
import logging

from django.urls import reverse
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

import api

LOG = logging.getLogger(__name__)


class MediaView(api.views.MediaView):
    """View for rendering an individual media item. Extends the DRF's media item view."""

    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'ui/media.html'

    def get(self, request, pk):
        response = super().get(request, pk)
        media_item = copy.copy(response.data)
        media_item['statisticsUrl'] = reverse('ui:media_item_analytics', args=[pk])
        response.data['media_item_json'] = json.dumps(media_item)
        return response


class MediaAnalyticsView(api.views.MediaAnalyticsView):
    """
    View for rendering an individual media item's analytics.
    Extends the DRF's media item analytics view.

    """
    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'ui/analytics.html'

    def get(self, request, pk):
        response = super().get(request, pk)
        return Response({'analytics_json': json.dumps(response.data)})
