"""
Views

"""
import logging

from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.serializers import Serializer as NullSerializer

from api import views as apiviews

from . import renderers
from . import serializers

LOG = logging.getLogger(__name__)


class ResourcePageMixin:
    """
    Mixin class for resource page views which simply renders the UI.

    """
    serializer_class = NullSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'


class MediaView(ResourcePageMixin, apiviews.MediaItemMixin, generics.RetrieveAPIView):
    """
    A media item. Specialised to render a JSON-LD structured data representation of the media item
    as well.

    """
    serializer_class = serializers.MediaItemPageSerializer
    template_name = 'ui/media.html'


class MediaItemRSSView(apiviews.MediaItemMixin, generics.RetrieveAPIView):
    """
    Retrieve an individual media item as RSS.

    IMPORTANT: we do not want this sort of feed to proliferate and so it is only available for
    media items which were imported from the old SMS.

    """
    # We cannot simply make use of the normal DRF content negotiation and format_suffix_patterns()
    # because this results in an additional "format" parameter being passed to the class which is
    # then used to reverse() URLs for hyperlinked resources such as channels. Since none of those
    # views support the format parameter, the reverse() call used by HyperlinkedIdentityField
    # fails.
    renderer_classes = [renderers.RSSRenderer]
    serializer_class = serializers.MediaItemRSSSerializer

    def get_queryset(self):
        return super().get_queryset().filter(downloadable_by_user=True, sms__isnull=False)

    def get_object(self):
        obj = super().get_object()
        # We need to render a list of entries with just this media item as a single entry. This is
        # a bit of a hacky way of doing this but it works.
        obj.self_list = [obj]
        return obj


class ChannelView(ResourcePageMixin, apiviews.ChannelMixin, generics.RetrieveAPIView):
    """A channel."""


class PlaylistView(ResourcePageMixin, apiviews.PlaylistMixin, generics.RetrieveAPIView):
    """A playlist"""


class PlaylistRSSView(apiviews.PlaylistMixin, generics.RetrieveAPIView):
    """
    Retrieve an individual playlist as RSS.

    """
    # We cannot simply make use of the normal DRF content negotiation and format_suffix_patterns()
    # because this results in an additional "format" parameter being passed to the class which is
    # then used to reverse() URLs for hyperlinked resources such as channels. Since none of those
    # views support the format parameter, the reverse() call used by HyperlinkedIdentityField
    # fails.
    renderer_classes = [renderers.RSSRenderer]
    serializer_class = serializers.PlaylistRSSSerializer

    def get_object(self):
        obj = super().get_object()
        obj.downloadable_media_items = (
            self.filter_media_item_qs(obj.ordered_media_item_queryset)
            .downloadable_by_user(self.request.user)
        )
        return obj
