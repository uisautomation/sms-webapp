"""
Views implementing the API endpoints.

"""
import copy
import logging
from collections import namedtuple

from django.conf import settings
from django.db import connection
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, pagination, filters

from smsjwplatform import jwplatform
import mediaplatform.models as mpmodels

from . import serializers


LOG = logging.getLogger(__name__)


class JWPAPIException(APIException):
    """
    DRF :py:exc:`APIException` sub-class which indicates that the request could not be handled
    because the JWPlatform API request failed.

    """
    status_code = 502  # Bad Gateway
    default_detail = 'Bad Gateway'
    default_code = 'jwplatform_api_error'


def check_api_call(response):
    """
    Take a response from a JWPlatform API call and raise :py:exc:`JWPAPIException` if the status
    was not ``ok``.

    """
    if response.get('status') == 'ok':
        return response

    LOG.error('API call error: %r', response)
    raise JWPAPIException()


class ProfileView(APIView):
    """
    Endpoint to retrieve the profile of the current user.

    """
    @swagger_auto_schema(
        responses={200: serializers.ProfileSerializer()}
    )
    def get(self, request):
        """Handle GET request."""
        urls = {'login': settings.LOGIN_URL}
        return Response(serializers.ProfileSerializer({
            'user': request.user, 'urls': urls,
        }).data)


class CollectionListView(APIView):
    """
    Endpoint to retrieve a list of collections.

    """
    @swagger_auto_schema(
        query_serializer=serializers.CollectionListQuerySerializer(),
        responses={200: serializers.CollectionListSerializer()}
    )
    def get(self, request):
        """Handle GET request."""
        client = jwplatform.get_jwplatform_client()

        query_serializer = serializers.CollectionListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        params = {}

        # Add default parameters
        params.update({
            'result_limit': 100,
        })

        # Add parameters from query
        for key in ['search']:
            if query_serializer.data.get(key) is not None:
                params[key] = query_serializer.data[key]

        # Add parameters which cannot be overridden
        params.update({
            'http_method': 'POST',
        })

        # Create a shallow copy of the response because we modify it below
        channel_list = copy.copy(check_api_call(jwplatform.Channel.list(params, client=client)))

        # Filter channels. They must have an SMS collection id (so have originated on the SMS).
        channel_list['channels'] = [
            channel for channel in channel_list['channels']
            if channel.collection_id is not None
        ]

        # TODO: filter channels by ACL - there is currently no processing of channel ACLs by the
        # sms2jwplayer scripts.

        return Response(serializers.CollectionListSerializer(channel_list).data)


class MediaListPagination(pagination.CursorPagination):
    page_size = 50


class MediaListSearchFilter(filters.SearchFilter):
    """
    Custom filter based on :py:class:`rest_framework.filters.SearchFilter` specialised to search
    :py:class:`mediaplatform.models.MediaItem` objects. If the "tags" field is specified in the
    view's ``search_fields`` attribute, then the tags field is dearched for any tag matching the
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


class MediaListView(generics.ListAPIView):
    """
    Endpoint to retrieve a list of media.

    """
    filter_backends = (filters.OrderingFilter, MediaListSearchFilter)
    ordering = '-published_at'
    ordering_fields = ('published_at',)
    pagination_class = MediaListPagination
    queryset = mpmodels.MediaItem.objects
    search_fields = ('title', 'description', 'tags')
    serializer_class = serializers.MediaSerializer

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .viewable_by_user(self.request.user)
            .select_related('jwp')
            .select_related('sms')
        )


class MediaView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve a single media item.

    """
    queryset = mpmodels.MediaItem.objects
    serializer_class = serializers.MediaDetailSerializer

    def get_queryset(self):
        return (
            super().get_queryset().all()
            .viewable_by_user(self.request.user)
            .select_related('jwp')
            .select_related('sms')
        )


# simple object for serialization of media_stats_by_day
MediaStatsByDay = namedtuple('MediaStatsByDay', ('day', 'num_hits'))


class MediaAnalyticsView(APIView):
    """
    Endpoint to retrieve the analytics for a single media item.

    """
    @swagger_auto_schema(
        responses={200: serializers.MediaAnalyticsSerializer()}
    )
    def get(self, request, pk):
        """Handle GET request."""

        media_item = (
            mpmodels.MediaItem.objects.filter(pk=pk)
            .viewable_by_user(request.user)
            .select_related('sms').first()
        )

        if not media_item:
            raise Http404

        cursor = get_cursor()
        cursor.execute(
            "SELECT day, num_hits FROM stats.media_stats_by_day WHERE media_id=%s",
            [media_item.sms.id]
        )
        analytics = [
            MediaStatsByDay(day=item[0], num_hits=item[1]) for item in cursor.fetchall()
        ]
        cursor.close()
        return Response(serializers.MediaAnalyticsSerializer(analytics, many=True).data)


def get_cursor():
    """Retrieve DB cursor. Method included for patching in tests"""
    return connection.cursor()
