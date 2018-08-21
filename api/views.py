"""
Views implementing the API endpoints.

"""
import logging

import automationlookup
from django.conf import settings
from django.db import models
from django_filters import rest_framework as df_filters
from rest_framework import generics, pagination, filters
import requests

import mediaplatform.models as mpmodels

from . import permissions
from . import serializers


LOG = logging.getLogger(__name__)


def get_profile(request):
    """
    Return an object representing what is known about a user from a reques. Contains two keys:
    ``user`` which is simply the user object from the request and ``person`` which is the lookup
    person resource for the user is non-anoymous.

    """
    obj = {'user': request.user}
    if not request.user.is_anonymous:
        try:
            obj['person'] = automationlookup.get_person(
                identifier=request.user.username,
                scheme=getattr(settings, 'LOOKUP_SCHEME', 'crsid'),
                fetch=['jpegPhoto'],
            )
        except requests.HTTPError as e:
            LOG.warning('Error fetching person: %s', e)
    return obj


class ProfileView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve the profile of the current user.

    """
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return get_profile(self.request)


class ListPagination(pagination.CursorPagination):
    page_size = 50


class ListMixinBase:
    """
    Base class for the various ListView mixin classes which ensures that the list only contains
    resources viewable by the user, annotates the resources with the viewable and editable
    flags and selects related JWPlatform and SMS objects.

    Sets permission_classes to :py:class:`~.permissions.MediaPlatformPermission` so that safe and
    unsafe operations are appropriately restricted.

    """
    permission_classes = [permissions.MediaPlatformPermission]

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .viewable_by_user(self.request.user)
            .annotate_viewable(self.request.user)
            .annotate_editable(self.request.user)
            .select_related('sms')
        )


class MediaItemListSearchFilter(filters.SearchFilter):
    """
    Custom filter based on :py:class:`rest_framework.filters.SearchFilter` specialised to search
    :py:class:`mediaplatform.models.MediaItem` objects. If the "tags" field is specified in the
    view's ``search_fields`` attribute, then the tags field is searched for any tag matching the
    lower cased search term.

    """

    def get_search_term(self, request):
        return request.query_params.get(self.search_param, '')

    def get_search_terms(self, request):
        return [self.get_search_term(request)]

    def filter_queryset(self, request, queryset, view):
        filtered_qs = super().filter_queryset(request, queryset, view)

        if 'tags' in getattr(view, 'search_fields', ()):
            search_term = self.get_search_term(request)
            filtered_qs |= queryset.filter(tags__contains=[search_term.lower()])

        return filtered_qs


class MediaItemListMixin(ListMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) media items. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.MediaItem.objects

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .select_related('jwp')
        )


class MediaItemMixin(MediaItemListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual media items. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """


def _user_playlists(request):
    """
    Return a queryset from a request which contains all the playlists which are viewable by the
    user making the request.

    """
    user = request.user if request is not None else None
    return mpmodels.Playlist.objects.all().viewable_by_user(user)


class MediaItemFilter(df_filters.FilterSet):
    class Meta:
        model = mpmodels.MediaItem
        fields = ('channel', 'playlist')

    playlist = df_filters.ModelChoiceFilter(
        label='Playlist', method='filter_playlist',
        help_text='Only media items from this playlist will be listed',
        queryset=_user_playlists)

    def filter_playlist(self, queryset, name, value):
        """
        Filter media items to only those which appear in a selected playlist. Since the playlist
        filter field is a ModelChoiceFilter, the "value" is the playlist object itself.

        """
        return queryset.filter(id__in=value.media_items)


class MediaItemListView(MediaItemListMixin, generics.ListCreateAPIView):
    """
    Endpoint to retrieve a list of media.

    """
    filter_backends = (filters.OrderingFilter, MediaItemListSearchFilter,
                       df_filters.DjangoFilterBackend)
    ordering = '-publishedAt'
    ordering_fields = ('publishedAt',)
    pagination_class = ListPagination
    search_fields = ('title', 'description', 'tags')
    serializer_class = serializers.MediaItemSerializer
    filterset_class = MediaItemFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(publishedAt=models.F('published_at'))


class MediaItemView(MediaItemMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve a single media item.

    """
    serializer_class = serializers.MediaItemDetailSerializer


class MediaItemUploadView(MediaItemMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint for retrieving an upload URL for a media item. Requires that the user have the edit
    permission for the media item. Should the upload URL be expired or otherwise unsuitable, a HTTP
    POST/PUT to this endpoint refreshes the URL.

    """
    # To access the upload API, the user must always have the edit permission.
    permission_classes = MediaItemListMixin.permission_classes + [
        permissions.MediaPlatformEditPermission
    ]
    serializer_class = serializers.MediaUploadSerializer

    # Make sure that the related upload_endpoint is fetched by the queryset
    def get_queryset(self):
        return super().get_queryset().select_related('upload_endpoint')


class MediaItemAnalyticsView(MediaItemMixin, generics.RetrieveAPIView):
    """
    Endpoint to retrieve the analytics for a single media item.

    """
    serializer_class = serializers.MediaItemAnalyticsListSerializer


class ChannelListMixin(ListMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) channels. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.Channel.objects


class ChannelMixin(ChannelListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual channels. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """


class ChannelListFilterSet(df_filters.FilterSet):
    class Meta:
        model = mpmodels.Channel
        fields = ('editable',)

    editable = df_filters.BooleanFilter(
        label='Editable', help_text='Filter by whether the user can edit this channel')


class ChannelListView(ChannelListMixin, generics.ListCreateAPIView):
    """
    Endpoint to retrieve a list of channels.

    """
    filter_backends = (
        filters.OrderingFilter, filters.SearchFilter, df_filters.DjangoFilterBackend)
    ordering = '-createdAt'
    ordering_fields = ('createdAt', 'title')
    pagination_class = ListPagination
    search_fields = ('title', 'description')
    serializer_class = serializers.ChannelSerializer
    filterset_class = ChannelListFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(createdAt=models.F('created_at'))


class ChannelView(ChannelMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve an individual channel.

    """
    serializer_class = serializers.ChannelDetailSerializer


class PlaylistListMixin(ListMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) playlists. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.Playlist.objects


class PlaylistMixin(PlaylistListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual playlists. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """


class PlaylistListFilterSet(df_filters.FilterSet):
    class Meta:
        model = mpmodels.Playlist
        fields = ('editable',)

    editable = df_filters.BooleanFilter(
        label='Editable', help_text='Filter by whether the user can edit this channel')


class PlaylistListView(PlaylistListMixin, generics.ListCreateAPIView):
    """
    Endpoint to retrieve a list of playlists.

    """
    filter_backends = (
        filters.OrderingFilter, filters.SearchFilter, df_filters.DjangoFilterBackend)
    ordering = '-updatedAt'
    ordering_fields = ('updatedAt', 'createdAt', 'title')
    pagination_class = ListPagination
    search_fields = ('title', 'description')
    serializer_class = serializers.PlaylistSerializer
    filter_fields = ('channel',)
    filterset_class = PlaylistListFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(createdAt=models.F('created_at'), updatedAt=models.F('updated_at'))


class PlaylistView(PlaylistMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve an individual playlists.

    """
    serializer_class = serializers.PlaylistDetailSerializer
