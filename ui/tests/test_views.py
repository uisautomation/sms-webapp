"""
Tests for views.

"""

from unittest import mock

from django.conf import settings
from django.test import TestCase

from django.urls import reverse


class ViewsTestCase(TestCase):

    @mock.patch('ui.views.DEFAULT_REQUESTS_SESSION.get')
    def test_success(self, mock_get):
        """checks that a media item is rendered successfully"""
        media_item = {}
        response = mock.Mock()
        response.ok = True
        response.content.decode.return_value = media_item
        mock_get.return_value = response

        # test
        r = self.client.get(reverse('ui:media', kwargs={'media_key': 'XYZ123'}))

        mock_get.assert_called_with(settings.MEDIA_API_URL + 'media/XYZ123')
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'ui/media.html')
        self.assertEqual(r.context['media_item'], media_item)

    @mock.patch('ui.views.DEFAULT_REQUESTS_SESSION.get')
    def test_video_not_found(self, mock_get):
        """checks that a video not found results in a 404"""
        response = mock.Mock()
        response.ok = False
        response.status_code = 404
        mock_get.return_value = response

        # test
        r = self.client.get(reverse('ui:media', kwargs={'media_key': 'XYZ123'}))

        mock_get.assert_called_with(settings.MEDIA_API_URL + 'media/XYZ123')
        self.assertEqual(r.status_code, 404)
