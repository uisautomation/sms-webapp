"""
Views

"""
import datetime
import json
import logging

from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

import api

LOG = logging.getLogger(__name__)


class MediaView(api.views.MediaView):
    """View for rendering an individual media item. Extends the DRF's media item view."""

    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'ui/media.html'

    def get(self, request, media_key):

        response = super().get(request, media_key)
        response.data['media_item_json'] = json.dumps(response.data)
        return response


class MediaAnalyticsView(api.views.MediaAnalyticsView):
    """
    View for rendering an individual media item's analytics.
    Extends the DRF's media item analytics view.

    """
    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'ui/analytics.html'

    def get(self, request, media_key):

        response = super().get(request, media_key)

        min_date = datetime.datetime.max
        max_date = datetime.datetime.min
        summed_by_date = {}

        # Here we sum up all views for a particular day and calculate the min and max dates.
        for item in response.data:
            date = datetime.datetime.strptime(item['date'], '%Y-%m-%d')
            views = summed_by_date.get(date, 0)
            summed_by_date[date] = views + item['views']
            min_date = min(min_date, date)
            max_date = max(max_date, date)

        if not summed_by_date:
            # the media has had no views
            return Response({'analytics_json': json.dumps([])})

        # Here we provide an ordered list of the views fill out missing days with zero views.
        day_count = (max_date - min_date).days + 1

        analytics = [
            {"date": date.strftime('%Y-%m-%d'), "views": summed_by_date.get(date, 0)}
            # Note we also add a zero data-point at either end of the data which makes the graph
            # look better in case of a single data-point.
            for date in (min_date + datetime.timedelta(n) for n in range(-1, day_count + 1))
        ]

        return Response({'analytics_json': json.dumps(analytics)})
