"""
Views implementing the API endpoints.

"""
import logging

import automationlookup
from django.conf import settings
from django.contrib.postgres.search import SearchRank, SearchQuery
from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django_filters import rest_framework as df_filters
from drf_yasg import inspectors, openapi
from rest_framework import generics, pagination, filters
from rest_framework.exceptions import ParseError
import requests

import mediaplatform.models as mpmodels
from mediaplatform_jwp.api import delivery

from . import permissions
from . import serializers


LOG = logging.getLogger(__name__)
#: Allowed poster image widths
POSTER_IMAGE_VALID_WIDTHS = [320, 480, 640, 720, 1280, 1920]

#: Default poster image width
POSTER_IMAGE_DEFAULT_WIDTH = 720

#: Allowed poster image extensions
POSTER_IMAGE_VALID_EXTENSIONS = ['jpg']


class ListPagination(pagination.CursorPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 300


class FullTextSearchFilter(filters.SearchFilter):
    """
    Custom filter based on :py:class:`rest_framework.filters.SearchFilter` specialised to search
    object with a full-text search SearchVectorField. Unlike the standard search filter, this class
    accepts only one search field to be set in search_fields.

    The filter *always* annotates the objects with a search rank. The name is "search_rank" by
    default but can be overridden by setting search_rank_annotation on the view. If the search is
    empty then this rank will always be zero.

    """
    def filter_queryset(self, request, queryset, view):
        search_terms = self.get_search_terms(request)
        search_fields = getattr(view, 'search_fields', None)
        search_rank_annotation = getattr(view, 'search_rank_annotation', 'search_rank')

        if search_fields and len(search_fields) > 1:
            raise ValueError('Can only handle a single search field')

        # If there are no search terms, shortcut the search to return the entire query set but
        # annotate it with a fake rank.
        if not search_fields or not search_terms:
            return queryset.annotate(**{
                search_rank_annotation: models.Value(0, output_field=models.FloatField())
            })

        # Otherwise, form a query which is the logical OR of all the query terms.
        query = SearchQuery(search_terms[0])
        for t in search_terms[1:]:
            query = query | SearchQuery(t)

        return queryset.annotate(**{
            search_rank_annotation: SearchRank(models.F(search_fields[0]), query)
        }).filter(**{search_fields[0]: query})


class ViewMixinBase:
    """
    A generic mixin class for API views which provides helper methods to filter querysets of
    MediaItem, Channel and Playlist objects for the request user and to be annotated with all of
    the fields required by the non-detail serialisers.

    Additionally, there are helper methods to annotate a query set with fields required by the
    detail serialisers.

    It also defines an appropriate permission class to forbid non-editors from performing "unsafe"
    operations on the objects.

    """
    permission_classes = [permissions.MediaPlatformPermission]

    def filter_media_item_qs(self, qs):
        """
        Filters a MediaItem queryset so that only the appropriate objects are returned for the
        user, annotates the objects with any fields required by the serialisers and selects any
        related objects used by the serialisers.

        """
        return (
            self._filter_permissions(qs)
            .select_related('sms')
            .select_related('jwp')
            .annotate_downloadable(self.request.user)
        )

    def filter_channel_qs(self, qs):
        """
        Filters a Channel queryset so that only the appropriate objects are returned for the user,
        annotates the objects with any fields required by the serialisers and selects any related
        objects used by the serialisers.

        """
        # For the moment we only need to respect permissions
        return self._filter_permissions(qs)

    def filter_playlist_qs(self, qs):
        """
        Filters a Playlist queryset so that only the appropriate objects are returned for the user,
        annotates the objects with any fields required by the serialisers and selects any related
        objects used by the serialisers.

        """
        # For the moment we only need to respect permissions
        return self._filter_permissions(qs)

    def filter_billing_account_qs(self, qs):
        """
        Filters a BillingAccount queryset so that only the appropriate objects are returned for the
        user, annotates the objects with any fields required by the serialisers and selects any
        related objects used by the serialisers.

        """
        # HACK: for the moment, billing accounts have no associated permissions so fake it so that
        # everyone can view them and no-one can edit them.
        return qs.annotate(
            viewable=models.Value(True, output_field=models.BooleanField()),
            editable=models.Value(False, output_field=models.BooleanField()),
        )

    def add_media_item_detail(self, qs):
        """
        Add any extra annotations to a MediaItem query set which are required to render the detail
        view via MediaItemDetailSerializer.

        """
        return qs.select_related('channel')

    def add_channel_detail(self, qs, name='item_count'):
        """
        Add any extra annotations to a Channel query set which are required to render the detail
        view via ChannelDetailSerializer.

        """
        items_qs = (
            self.filter_media_item_qs(mpmodels.MediaItem.objects.all())
            .filter(channel=models.OuterRef('pk'))
            .values('channel')
            .annotate(count=models.Count('*'))
            .values('count')
        )
        return qs.annotate(**{
            name: models.Subquery(items_qs, output_field=models.BigIntegerField())
        })

    def add_playlist_detail(self, qs):
        """
        Add any extra annotations to a Playlist query set which are required to render the detail
        view via PlaylistDetailSerializer.

        """
        return qs.select_related('channel')

    def _filter_permissions(self, qs):
        """
        Filter the passed queryset so that only items viewable by the request user are present and
        that the viewable and editable annotations are added. Works for MediaItem, Channel and
        Playlist.

        """
        # We use qs.all() here because we want to allow a manager object (e.g. MediaItem.objects)
        # to be passed as well.
        return (
            qs.all()
            .viewable_by_user(self.request.user)
            .annotate_viewable(self.request.user)
            .annotate_editable(self.request.user)
        )

    def get_profile(self):
        """
        Return an object representing what is known about a user from the request. The object can
        eb serialised with :py:class:`api.serializers.ProfileSerializer`.

        """
        obj = {
            'user': self.request.user,
            'channels': self.add_channel_detail(
                self.filter_channel_qs(mpmodels.Channel.objects.all())
                .editable_by_user(self.request.user)
            ),
        }
        if not self.request.user.is_anonymous:
            try:
                obj['person'] = automationlookup.get_person(
                    identifier=self.request.user.username,
                    scheme=getattr(settings, 'LOOKUP_SCHEME', 'crsid'),
                    fetch=['jpegPhoto'],
                )
            except requests.HTTPError as e:
                LOG.warning('Error fetching person: %s', e)
        return obj


class ProfileView(ViewMixinBase, generics.RetrieveAPIView):
    """
    Endpoint to retrieve the profile of the current user.

    """
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.get_profile()


class MediaItemListMixin(ViewMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) media items. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.MediaItem.objects

    def get_queryset(self):
        return self.filter_media_item_qs(super().get_queryset())


class MediaItemMixin(MediaItemListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual media items. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """
    def get_queryset(self):
        return self.add_media_item_detail(super().get_queryset())


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
    List and search Media items. If no other ordering is specified, results are returned in order
    of decreasing search relevance (if there is any search) and then by decreasing publication
    date.

    """
    filter_backends = (filters.OrderingFilter, FullTextSearchFilter,
                       df_filters.DjangoFilterBackend)
    # The default ordering is by search rank first and then publication date. If no search is used,
    # the rank is a fixed value and the publication date dominates.
    ordering = ('-search_rank', '-publishedAt')
    ordering_fields = ('publishedAt', 'updatedAt')
    pagination_class = ListPagination
    search_fields = ('text_search_vector',)
    serializer_class = serializers.MediaItemSerializer
    filterset_class = MediaItemFilter

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(publishedAt=models.F('published_at'), updatedAt=models.F('updated_at'))


class MediaItemView(MediaItemMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve a single media item.

    """
    serializer_class = serializers.MediaItemDetailSerializer


class MediaItemUploadView(MediaItemMixin, generics.UpdateAPIView):
    """
    Endpoint for retrieving an upload URL for a media item. Requires that the user have the edit
    permission for the media item. A HTTP PUT to this endpoint can be used to retrieve an upload
    URL which can then have the media file POST-ed to it.

    """
    # To access the upload API, the user must always have the edit permission.
    permission_classes = MediaItemListMixin.permission_classes + [
        permissions.MediaPlatformEditPermission
    ]
    serializer_class = serializers.MediaUploadSerializer

    # Make sure that the related upload_endpoint is fetched by the queryset
    def get_queryset(self):
        return super().get_queryset().select_related('upload_endpoint')


class MediaItemSourceViewInspector(inspectors.ViewInspector):
    def get_operation(self, operation_keys):
        return openapi.Operation(
            operation_id='media_source',
            responses=openapi.Responses(
                {302: openapi.Response(description='Media source stream')}
            ),
            parameters=[
                openapi.Parameter(
                    name='mimeType', in_=openapi.IN_QUERY,
                    description='MIME type of media source',
                    type=openapi.TYPE_STRING
                ),
                openapi.Parameter(
                    name='width', in_=openapi.IN_QUERY,
                    description='Width of media source',
                    type=openapi.TYPE_INTEGER
                ),
                openapi.Parameter(
                    name='height', in_=openapi.IN_QUERY,
                    description='Height of media source',
                    type=openapi.TYPE_INTEGER
                ),
            ],
            tags=['media'],
        )


class MediaItemSourceView(MediaItemMixin, generics.RetrieveAPIView):
    """
    Endpoint to retrieve a media item source stream

    """
    swagger_schema = MediaItemSourceViewInspector

    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()

        # Check if user can download media item
        if not item.downloadable_by_user:
            raise Http404()

        mime_type = request.GET.get('mimeType')
        width = request.GET.get('width')
        height = request.GET.get('height')

        try:
            if width is not None:
                width = int(width)
            if height is not None:
                height = int(height)
        except ValueError:
            raise ParseError()

        if mime_type is None and width is None and height is None:
            # If nothing was specified, return the "best" source.
            video_sources = [
                source for source in item.sources
                if source.mime_type.startswith('video/') and source.height is not None
            ]
            audio_sources = [
                source for source in item.sources
                if source.mime_type.startswith('audio/')
            ]

            if len(video_sources) == 0 and len(audio_sources) != 0:
                # No video sources, return any of the audio sources
                return redirect(audio_sources.pop().url)
            elif len(video_sources) != 0:
                # Sort videos by descending height
                return redirect(sorted(video_sources, key=lambda s: -s.height)[0].url)
        else:
            for source in item.sources:
                if (source.mime_type == mime_type and source.width == width
                        and source.height == height):
                    return redirect(source.url)

        raise Http404()


class MediaItemAnalyticsView(MediaItemMixin, generics.RetrieveAPIView):
    """
    Endpoint to retrieve the analytics for a single media item.

    """
    serializer_class = serializers.MediaItemAnalyticsListSerializer


class MediaItemPosterViewInspector(inspectors.ViewInspector):
    def get_operation(self, operation_keys):
        return openapi.Operation(
            operation_id='media_poster',
            responses=openapi.Responses(
                {302: openapi.Response(description='Media poster image')}
            ),
            parameters=[
                openapi.Parameter(
                    name='width', in_=openapi.IN_PATH,
                    description='Desired width of image.',
                    type=openapi.TYPE_INTEGER,
                    enum=POSTER_IMAGE_VALID_WIDTHS,
                ),
                openapi.Parameter(
                    name='extension', in_=openapi.IN_PATH,
                    description='Desired format of image.',
                    type=openapi.TYPE_STRING,
                    enum=POSTER_IMAGE_VALID_EXTENSIONS,
                ),
            ],
            tags=['media'],
        )


class MediaItemPosterView(MediaItemMixin, generics.RetrieveAPIView):
    """
    Retrieve a poster image for a media item.

    """
    swagger_schema = MediaItemPosterViewInspector

    def retrieve(self, request, *args, **kwargs):
        jwp = getattr(self.get_object(), 'jwp', None)
        if jwp is None:
            raise Http404()

        # Retrieve and parse parameters
        width = kwargs.get('width')
        extension = kwargs.get('extension')
        try:
            if width is not None:
                width = int(width)
        except ValueError:
            raise ParseError()

        # Check width has a valid value
        if width not in POSTER_IMAGE_VALID_WIDTHS:
            raise Http404()

        if extension not in POSTER_IMAGE_VALID_EXTENSIONS:
            raise Http404()

        return redirect(delivery.Video({'key': jwp.key}).get_poster_url(width=width))


class ChannelListMixin(ViewMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) channels. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.Channel.objects

    def get_queryset(self):
        return self.filter_channel_qs(super().get_queryset())


class ChannelMixin(ChannelListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual channels. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """
    def get_queryset(self):
        return self.add_channel_detail(super().get_queryset())


class ChannelListFilterSet(df_filters.FilterSet):
    class Meta:
        model = mpmodels.Channel
        fields = ('editable',)

    editable = df_filters.BooleanFilter(
        label='Editable', help_text='Filter by whether the user can edit this channel')


class ChannelListView(ChannelListMixin, generics.ListCreateAPIView):
    """
    Endpoint to retrieve a list of channels.
    List and search Channels. If no other ordering is specified, results are returned in order
    of decreasing search relevance (if there is any search) and then by decreasing update
    date.

    """
    filter_backends = (
        filters.OrderingFilter, FullTextSearchFilter, df_filters.DjangoFilterBackend)
    # The default ordering is by search rank first and then update date. If no search is used,
    # the rank is a fixed value and the update date dominates.
    ordering = ('-search_rank', '-updatedAt')
    ordering_fields = ('updatedAt', 'createdAt', 'title')
    pagination_class = ListPagination
    search_fields = ('text_search_vector',)
    serializer_class = serializers.ChannelSerializer
    filterset_class = ChannelListFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(createdAt=models.F('created_at'), updatedAt=models.F('updated_at'))


class ChannelView(ChannelMixin, generics.RetrieveUpdateAPIView):
    """
    Endpoint to retrieve an individual channel.

    """
    serializer_class = serializers.ChannelDetailSerializer


class PlaylistListMixin(ViewMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    (and possibly creating/deleting) playlists. Use this mixin with ListAPIView or
    ListCreateAPIView to form a concrete view class.

    """
    queryset = mpmodels.Playlist.objects

    def get_queryset(self):
        return self.filter_playlist_qs(super().get_queryset())


class PlaylistMixin(PlaylistListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual playlists. Use this mixin with RetrieveAPIView
    or RetrieveUpdateAPIView to form a concrete view class.

    """
    def get_queryset(self):
        return self.add_playlist_detail(super().get_queryset())

    def get_object(self):
        obj = super().get_object()

        # annotate object with media for user
        obj.media_for_user = self.filter_media_item_qs(obj.ordered_media_item_queryset)

        return obj


class PlaylistListFilterSet(df_filters.FilterSet):
    class Meta:
        model = mpmodels.Playlist
        fields = ('editable',)

    editable = df_filters.BooleanFilter(
        label='Editable', help_text='Filter by whether the user can edit this channel')


class PlaylistListView(PlaylistListMixin, generics.ListCreateAPIView):
    """
    Endpoint to retrieve a list of playlists.
    List and search Playlists. If no other ordering is specified, results are returned in order
    of decreasing search relevance (if there is any search) and then by decreasing update
    date.

    """
    filter_backends = (
        filters.OrderingFilter, FullTextSearchFilter, df_filters.DjangoFilterBackend)
    # The default ordering is by search rank first and then update date. If no search is used,
    # the rank is a fixed value and the update date dominates.
    ordering = ('-search_rank', '-updatedAt')
    ordering_fields = ('updatedAt', 'createdAt', 'title')
    pagination_class = ListPagination
    search_fields = ('text_search_vector',)
    serializer_class = serializers.PlaylistSerializer
    filter_fields = ('channel',)
    filterset_class = PlaylistListFilterSet

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(createdAt=models.F('created_at'), updatedAt=models.F('updated_at'))


class PlaylistView(PlaylistMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint to retrieve an individual playlists.

    """
    serializer_class = serializers.PlaylistDetailSerializer

    def get_object(self):
        obj = super().get_object()

        # Add a list of all the media which is viewable by the current user. This is used by the
        # detail serialiser.
        obj.media = obj.ordered_media_item_queryset.viewable_by_user(self.request.user)
        return obj


class BillingAccountListMixin(ViewMixinBase):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for listing
    billing accounts.

    """
    queryset = mpmodels.BillingAccount.objects

    def get_queryset(self):
        return self.filter_billing_account_qs(super().get_queryset())


class BillingAccountMixin(BillingAccountListMixin):
    """
    A mixin class for DRF generic views which has all of the specialisations necessary for
    retrieving (and possibly updating) individual nilling accounts.

    """


class BillingAccountListFilterSet(df_filters.FilterSet):
    class Meta:
        model = mpmodels.BillingAccount
        fields = ('canCreateChannels',)

    canCreateChannels = df_filters.BooleanFilter(
        field_name='can_create_channels',
        label='Can create channels',
        help_text=(
            '"true" or "false". Filter by whether the user can create channels for '
            'this billing account')
    )


class BillingAccountListView(BillingAccountListMixin, generics.ListAPIView):
    """
    Billing accounts.

    """
    filter_backends = (filters.OrderingFilter, df_filters.DjangoFilterBackend)
    ordering = ('-updatedAt',)
    ordering_fields = ('updatedAt', 'createdAt', 'lookupInstid')
    pagination_class = ListPagination
    serializer_class = serializers.BillingAccountSerializer
    filterset_class = BillingAccountListFilterSet

    def get_queryset(self):
        return (
            super().get_queryset()
            # Required for ordering filter
            .annotate(updatedAt=models.F('updated_at'))
            .annotate(createdAt=models.F('created_at'))
            .annotate(lookupInstid=models.F('lookup_instid'))
            # Required for canCreateChannels filter
            .annotate_can_create_channels(self.request.user)
        )


class BillingAccountView(BillingAccountMixin, generics.RetrieveAPIView):
    """
    Billing account.

    """
    serializer_class = serializers.BillingAccountDetailSerializer
