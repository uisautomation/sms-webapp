# from dateutil.utils import today
# from django.conf import settings
from django.urls import reverse
from feedgen.feed import FeedGenerator
from rest_framework import renderers


MIME_TYPE_MAPPING = {'video': 'video/mp4', 'audio': 'audio/mp4'}


class RSSRenderer(renderers.BaseRenderer):
    """
    A specialised renderer for playlist resources which matches the iTunes RSS feed specification
    at https://help.apple.com/itc/podcasts_connect/#/itc1723472cb.

    """
    media_type = 'application/rss+xml'
    format = 'rss'

    def render(self, data, media_type=None, renderer_context=None):
        try:
            # There must be a request object in order to build absolute URIs.
            request = renderer_context['request']
        except KeyError:
            raise RuntimeError('Renderer context has no request object')

        # Prepare the feed generator object.
        fg = FeedGenerator()
        fg.load_extension('podcast')

        # Playlist wrapper.
        fg.id(request.build_absolute_uri(reverse('ui:playlist', kwargs={'pk': data['id']})))
        fg.title(data['title'])

        # Description. Feedgen will raise exception if the description is empty
        fg.description(_ensure_non_empty(data['description']))
        fg.podcast.itunes_summary(_ensure_non_empty(data['description']))

        # Self link.
        fg.link(
            href=request.build_absolute_uri(reverse('api:playlist', kwargs={'pk': data['id']})),
            rel='self'
        )

        # TODO: Missing fields from playlists: author, contributors, logo, subtitle, and language.

        # Add entries
        for media_item in data['mediaForUser']:
            # Skip non-downloadable media items
            if not media_item['downloadable']:
                continue

            fe = fg.add_entry()

            # The item id. We don't set permaLink for the moment because URLs may change during the
            # alpha.
            fe.id(request.build_absolute_uri(
                reverse('api:media_item', kwargs={'pk': media_item['id']})
            ))

            # Set basic metadata. Feedgen will raise an exception if the description is empty.
            fe.title(media_item['title'])
            fe.description(_ensure_non_empty(media_item['description']))
            fe.summary(_ensure_non_empty(media_item['description']))

            # RSS only supports one link with nothing but a URL. So for the RSS link element the
            # last link with rel=alternate is used. We link to the UI view even though we use the
            # API endpoint as the id.
            fe.link(href=request.build_absolute_uri(
                reverse('ui:media_item', kwargs={'pk': media_item['id']})
            ))

            # Publication date.
            fe.pubDate(media_item['publishedAt'])

            # Free-text copyright field.
            fe.rights(media_item['copyright'])

            # When the item was last updated.
            fe.updated(media_item['updatedAt'])

            # Image. Note: iTunes *requires* this to end in ".jpg" or ".png" which is annoying.
            fe.podcast.itunes_image(request.build_absolute_uri(
                reverse('api:media_poster', kwargs={
                    'pk': media_item['id'], 'width': 1920, 'extension': 'jpg'
                })
            ))

            # Duration in seconds rounded down.
            fe.podcast.itunes_duration(int(media_item['duration']))

            # The actual downloads themselves.
            #
            # TODO: at the moment, getting the source information requires a JWP delivery API call
            # for each media item. To avoid this we should probably cache source information in
            # the database. For the time being we "fake" a source by assuming the mimetype based on
            # the type of the item.
            best_source_url = request.build_absolute_uri(
                reverse('api:media_source', kwargs={'pk': media_item['id']})
            )
            fe.enclosure(
                url=best_source_url,
                type=MIME_TYPE_MAPPING.get(media_item['type'], 'application/octet-stream')
            )

        # Render the feed.
        return fg.rss_str(pretty=True)


def _ensure_non_empty(s):
    """
    Take a str or None and return a non-empty string.

    """
    return ' ' if s is None or s == '' else s
