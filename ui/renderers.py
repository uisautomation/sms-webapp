from feedgen.feed import FeedGenerator
from rest_framework import renderers

# if no author is set for the item or channel this default is used
DEFAULT_AUTHOR = 'Cambridge University'


class RSSRenderer(renderers.BaseRenderer):
    """
    A specialised renderer for RSS feeds which match the iTunes RSS feed specification
    at https://help.apple.com/itc/podcasts_connect/#/itc1723472cb.

    Expects that the data is of the following form:

    .. code:: python

        {
            'url': str,  # link back to resource
            'title': str,
            'description': str,
            'entries': [
                'url': str,
                'imageUrl': str,  # must end in .jpg or .png
                'title': str,
                'description': str,
                'duration': int,  # in seconds
                'rights': str,
                'published_at': datetime,
                'updated_at': datetime,
                'enclosures': [
                    {
                        'url': str,
                        'mime_type': str,
                    }, # ...
                ],
            ],
        }

    """
    media_type = 'application/rss+xml'
    format = 'rss'

    def render(self, data, media_type=None, renderer_context=None):
        renderer_context = renderer_context or {}
        response = renderer_context['response']

        if response.exception:
            return f'Error: {response.status_code}'

        # If we get this far, the response is not an error and we can render the RSS feed.

        # Prepare the feed generator object.
        fg = FeedGenerator()
        fg.load_extension('podcast')

        # Playlist wrapper.
        fg.id(data['url'])
        fg.title(data['title'])

        # Description. Feedgen will raise exception if the description is empty
        fg.description(_ensure_non_empty(data['description']))
        fg.podcast.itunes_summary(_ensure_non_empty(data['description']))

        # The author.
        fg.podcast.itunes_author(data['author'] if data['author'] else DEFAULT_AUTHOR)

        # Self link.
        fg.link(href=data['url'])

        # TODO: Missing fields from playlists: contributors, logo, subtitle, and language.

        # Add entries
        for entry in data['entries']:
            fe = fg.add_entry()

            # The item id. We don't set permaLink for the moment because URLs may change during the
            # alpha.
            fe.id(entry['url'])

            # Set basic metadata. Feedgen will raise an exception if the description is empty.
            fe.title(entry['title'])
            fe.description(_ensure_non_empty(entry['description']))
            fe.summary(_ensure_non_empty(entry['description']))

            # The author.
            fe.podcast.itunes_author(entry['author'] if entry['author'] else DEFAULT_AUTHOR)

            # RSS only supports one link with nothing but a URL. So for the RSS link element the
            # last link with rel=alternate is used. We link to the UI view even though we use the
            # API endpoint as the id.
            fe.link(href=entry['url'])

            # Publication date.
            fe.pubDate(entry['published_at'])

            # Free-text copyright field.
            fe.rights(entry['rights'])

            # When the item was last updated.
            fe.updated(entry['updated_at'])

            # Image. Note: iTunes *requires* this to end in ".jpg" or ".png" which is annoying.
            fe.podcast.itunes_image(entry['imageUrl'])

            # Duration in seconds.
            fe.podcast.itunes_duration(entry['duration'])

            # The actual downloads themselves.
            for enclosure in entry['enclosures']:
                fe.enclosure(url=enclosure['url'], type=enclosure['mime_type'])

        # Render the feed.
        return fg.rss_str(pretty=True)


def _ensure_non_empty(s):
    """
    Take a str or None and return a non-empty string.

    """
    return ' ' if s is None or s == '' else s
