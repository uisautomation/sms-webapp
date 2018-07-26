"""
Tests for views.

"""
import json
import datetime
from unittest import mock

from django.test import TestCase

from django.urls import reverse

import smsjwplatform.jwplatform as api
from api.tests.test_views import DELIVERY_VIDEO_FIXTURE
from legacysms.models import MediaStatsByDay


class MediaViewTestCase(TestCase):

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    def test_success(self, mock_from_id):
        """checks that a media item is rendered successfully"""
        mock_from_id.return_value = api.DeliveryVideo(DELIVERY_VIDEO_FIXTURE)

        # test
        r = self.client.get(reverse('ui:media_item', kwargs={'media_key': 'XYZ123'}))

        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/media.html')
        self.assertEqual(r.context['title'], 'Mock 1')
        media_item_json = json.loads(r.context['media_item_json'])
        self.assertEqual(
            media_item_json['poster_image_url'], 'https://cdn.jwplayer.com/thumbs/mock1-720.jpg'
        )

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    def test_video_not_found(self, mock_from_id):
        """checks that a video not found results in a 404"""
        mock_from_id.side_effect = api.VideoNotFoundError

        # test
        r = self.client.get(reverse('ui:media_item', kwargs={'media_key': 'XYZ123'}))

        self.assertEqual(r.status_code, 404)

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    def test_no_access_to_video(self, mock_from_id):
        """Check that a 403 is returned the caller isn't the ACL"""
        mock_from_id.return_value = api.DeliveryVideo(
            {**DELIVERY_VIDEO_FIXTURE, 'sms_acl': 'acl:CAM:'}
        )

        # test
        r = self.client.get(reverse('ui:media_item', kwargs={'media_key': 'XYZ123'}))

        self.assertEqual(r.status_code, 403)


class MediaAnalyticsViewTestCase(TestCase):

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    @mock.patch('legacysms.models.MediaStatsByDay.objects.filter')
    def test_success(self, mock_filter, mock_from_id):
        """checks that a media item's analytics are rendered successfully"""

        mock_filter.return_value = [
            MediaStatsByDay(day=datetime.date(2018, 4, 17), num_hits=3),
            MediaStatsByDay(day=datetime.date(2018, 3, 22), num_hits=4),
            MediaStatsByDay(day=datetime.date(2018, 3, 22), num_hits=1),
        ]
        mock_from_id.return_value = api.DeliveryVideo(DELIVERY_VIDEO_FIXTURE)

        # test
        r = self.client.get(reverse('ui:media_item_analytics', kwargs={'media_key': 'XYZ123'}))

        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/analytics.html')
        analytics_json = json.loads(r.context['analytics_json'])
        self.assertEqual(len(analytics_json), 29)

        self.assertEqual(analytics_json[1]['date'], datetime.datetime(2018, 3, 22).timestamp())
        self.assertEqual(analytics_json[1]['views'], 5)
        self.assertEqual(analytics_json[27]['date'], datetime.datetime(2018, 4, 17).timestamp())
        self.assertEqual(analytics_json[27]['views'], 3)

        # check zero added at beginning
        self.assertEqual(analytics_json[0]['date'], datetime.datetime(2018, 3, 21).timestamp())
        self.assertEqual(analytics_json[0]['views'], 0)
        # check padding
        for i in range(2, 26):
            self.assertEqual(analytics_json[i]['views'], 0)
        # check zero added at end
        self.assertEqual(analytics_json[28]['date'], datetime.datetime(2018, 4, 18).timestamp())
        self.assertEqual(analytics_json[28]['views'], 0)

    @mock.patch('smsjwplatform.jwplatform.DeliveryVideo.from_key')
    @mock.patch('legacysms.models.MediaStatsByDay.objects.filter')
    def test_no_analytics(self, mock_filter, mock_from_id):
        """checks that a media item with no analytics is handled correctly"""

        mock_filter.return_value = []
        mock_from_id.return_value = api.DeliveryVideo(DELIVERY_VIDEO_FIXTURE)

        # test
        r = self.client.get(reverse('ui:media_item_analytics', kwargs={'media_key': 'XYZ123'}))

        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/analytics.html')
        analytics_json = json.loads(r.context['analytics_json'])
        self.assertEqual(len(analytics_json), 0)
