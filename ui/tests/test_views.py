"""
Tests for views.

"""
import json
from unittest import mock
from unittest.mock import Mock

from django.urls import reverse

import smsjwplatform.jwplatform as api
from api.tests.test_views import ViewTestCase, DELIVERY_VIDEO_FIXTURE


class ViewsTestCase(ViewTestCase):

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    def test_success(self, mock_from_id):
        """checks that a media item is rendered successfully"""
        mock_from_id.return_value = api.DeliveryVideo(DELIVERY_VIDEO_FIXTURE)
        item = self.non_deleted_media.get(id='populated')

        # test
        r = self.client.get(reverse('ui:media_item', kwargs={'pk': item.pk}))

        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/media.html')
        self.assertEqual(r.context['name'], item.title)
        media_item_json = json.loads(r.context['media_item_json'])
        self.assertIn(
            'https://cdn.jwplayer.com/thumbs/{}-1280.jpg'.format(item.jwp.key),
            media_item_json['thumbnailUrl'],
        )

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    def test_video_not_found(self, mock_from_id):
        """checks that a video not found results in a 404"""
        mock_from_id.side_effect = api.VideoNotFoundError

        # test
        r = self.client.get(reverse('ui:media_item', kwargs={'pk': 'this-does-not-exist'}))

        self.assertEqual(r.status_code, 404)

    # TODO: add ACL checks here


class MediaAnalyticsViewTestCase(ViewTestCase):

    @mock.patch('api.views.get_cursor')
    def test_success(self, mock_get_cursor):
        """checks that a media item's analytics are rendered successfully"""

        cursor = Mock()
        cursor.fetchall.return_value = []
        mock_get_cursor.return_value = cursor

        item = self.non_deleted_media.get(id='populated')

        # test
        r = self.client.get(reverse('ui:media_item_analytics', kwargs={'pk': item.pk}))

        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/analytics.html')
        analytics_json = json.loads(r.context['analytics_json'])
        self.assertEqual(len(analytics_json), 0)
