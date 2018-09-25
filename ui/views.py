"""
Views

"""
import logging

from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer

from api import views as apiviews

from . import renderers
from . import serializers

LOG = logging.getLogger(__name__)


class MediaView(apiviews.MediaItemMixin, generics.RetrieveAPIView):
    """View for rendering an individual media item. Extends the DRF's media item view."""
    serializer_class = serializers.MediaItemPageSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ui/media.html'


class MediaItemAnalyticsView(apiviews.MediaItemMixin, generics.RetrieveAPIView):
    """
    View for rendering an individual media item's analytics.
    Extends the DRF's media item analytics view.

    """
    serializer_class = serializers.ResourcePageSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ui/resource.html'


class ChannelView(apiviews.ChannelMixin, generics.RetrieveAPIView):
    """View for rendering an individual channel. Extends the DRF's channel view."""
    serializer_class = serializers.ChannelPageSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ui/resource.html'


class PlaylistView(apiviews.PlaylistMixin, generics.RetrieveAPIView):
    """View for rendering an individual playlist. Extends the DRF's channel view."""
    serializer_class = serializers.PlaylistPageSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'ui/resource.html'


class PlaylistRSSView(apiviews.PlaylistView):
    """
    Endpoint to retrieve an individual playlists as RSS. We specialise PlaylistView with a single
    renderer class.

    """
    # We cannot simply make use of the normal DRF content negotiation and format_suffix_patterns()
    # because this results in an additional "format" parameter being passed to the class which is
    # then used to reverse() URLs for hyperlinked resources such as channels. Since none of those
    # views support the format parameter, the reverse() call fails.

    renderer_classes = [renderers.RSSRenderer]
