import logging

from django.conf import settings
from rest_framework import serializers

from smsjwplatform import jwplatform

LOG = logging.getLogger(__name__)


class SourceSerializer(serializers.Serializer):
    """
    A download source for a particular media type.

    """
    type = serializers.CharField(help_text="The resource's MIME type")
    url = serializers.URLField(source='file', help_text="The resource's URL")
    width = serializers.IntegerField(help_text='The video width', required=False)
    height = serializers.IntegerField(help_text='The video height', required=False)


class MediaSerializer(serializers.Serializer):
    """
    An individual media item.

    """
    id = serializers.CharField(source='key', help_text='Unique id for the media')
    title = serializers.CharField(help_text='Title of media')
    description = serializers.CharField(help_text='Description of media')
    published_at_timestamp = serializers.IntegerField(
        source='date', help_text='Unix-style UTC timestamp of publication time')
    poster_image_url = serializers.SerializerMethodField(
        help_text='A URL of a thumbnail/poster image for the media'
    )
    duration = serializers.FloatField(help_text='Duration of the media in seconds')
    ui_url = serializers.SerializerMethodField(
        help_text='A URL for the media item. This is a URL for the media UI, not a resource URL.'
    )
    player_url = serializers.SerializerMethodField(
        help_text='A URL to retrieve an embeddable player for the media item.'
    )
    sources = SourceSerializer(
        help_text='A collection of download URLs for different media types.',
        required=False, many=True
    )
    legacy_stats_url = serializers.SerializerMethodField(
        help_text='A URL linking to the stats page in the legacy SMS app for the media item.'
    )

    def get_ui_url(self, obj):
        return '/media/{[key]}'.format(obj)

    def get_player_url(self, obj):
        return jwplatform.player_embed_url(
            obj['key'], settings.JWPLATFORM_EMBED_PLAYER_KEY, 'html',
            settings.JWPLATFORM_CONTENT_BASE_URL
        )

    def get_poster_image_url(self, obj):
        return obj.get_poster_url()

    def get_legacy_stats_url(self, obj):
        if not obj.media_id:
            return None
        return 'https://sms.cam.ac.uk/media/{.media_id}/statistics'.format(obj)


class MediaListSerializer(serializers.Serializer):
    """
    A media list response.

    """
    results = MediaSerializer(many=True, source='videos')
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    total = serializers.IntegerField()


class MediaListQuerySerializer(serializers.Serializer):
    """
    A media list query.

    """
    search = serializers.CharField(
        required=False,
        help_text='Free text search for media item'
    )

    order_by = serializers.ChoiceField(
        choices=[
            # As we expose other things from the JWPlatform API, add them here.
            ('date', 'Publication date'),
        ],
        default='date',
        help_text='Specify ordering for items'
    )

    direction = serializers.ChoiceField(
        choices=[('asc', 'Ascending'), ('desc', 'Descending')], default='desc',
        help_text='Direction of item ordering'
    )


class CollectionSerializer(serializers.Serializer):
    """
    An individual collection.

    """
    id = serializers.CharField(source='key', help_text='Unique id for the collection')
    title = serializers.CharField(help_text='Title of collection')
    description = serializers.CharField(help_text='Description of collection')
    poster_image_url = serializers.SerializerMethodField(
        help_text='A URL of a thumbnail/poster image for the collection')
    ui_url = serializers.SerializerMethodField(
        help_text=(
            'A URL for the collection. This is a URL for the collection UI, not a resource URL.'
        )
    )

    def get_ui_url(self, obj):
        return 'https://sms.cam.ac.uk/collection/{.collection_id}'.format(obj)

    def get_poster_image_url(self, obj):
        return obj.get_poster_url()


class CollectionListSerializer(serializers.Serializer):
    """
    A collection list response.

    """
    results = CollectionSerializer(many=True, source='channels')
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    total = serializers.IntegerField()


class CollectionListQuerySerializer(serializers.Serializer):
    """
    A collection list query.

    """
    search = serializers.CharField(
        required=False,
        help_text='Free text search for collection'
    )


class ProfileSerializer(serializers.Serializer):
    """
    The profile of the current user.

    """
    is_anonymous = serializers.BooleanField(source='user.is_anonymous')
    username = serializers.CharField(source='user.username')
    urls = serializers.DictField()
