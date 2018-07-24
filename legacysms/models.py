from django.db import models


class MediaItem(models.Model):
    """
    A media item hosted on the legacy SMS.

    """
    #: SMS media id
    id = models.BigIntegerField(primary_key=True, editable=False, help_text='Legacy SMS media id')

    #: Corresponding :py:class:`mediaplatform.MediaItem`. Accessible from the
    #: :py:class:`mediaplatform.MediaItem` model via the ``sms`` field. This can be NULL if there
    #: is no corresponding media item hosted by the Media Platform.
    item = models.OneToOneField(
        'mediaplatform.MediaItem', related_name='sms', editable=False,
        on_delete=models.SET_NULL, null=True)

    #: The last updated at time from the legacy SMS. Used to determine which items need updating.
    #: Some SMS object have this set to NULL, so we should allow it too.
    last_updated_at = models.DateTimeField(
        help_text='Last updated at time from SMS', editable=False, null=True)

    def __str__(self):
        return 'Legacy SMS media item {}'.format(self.id)


class Collection(models.Model):
    """
    A collection hosted on the legacy SMS.

    """
    #: SMS collection id
    id = models.BigIntegerField(
        primary_key=True, editable=False, help_text='Legacy SMS collection id')

    #: Corresponding :py:class:`mediaplatform.Collection`. Accessible from the
    #: :py:class:`mediaplatform.Collection` model via the ``sms`` field. This can be NULL if there
    #: is no corresponding collection hosted by the Media Platform.
    collection = models.OneToOneField(
        'mediaplatform.Collection', related_name='sms', on_delete=models.SET_NULL, null=True,
        editable=False)

    #: The last updated at time from the legacy SMS. Used to determine which collections need
    #: updating. Some SMS object have this set to NULL, so we should allow it too.
    last_updated_at = models.DateTimeField(
        help_text='Last updated at time from SMS', editable=False, null=True)

    def __str__(self):
        return 'Legacy SMS collection {}'.format(self.id)


class MediaStatsByDay(models.Model):
    """A model representing an number of views of a legacy media item on a particular day."""

    media_id = models.BigIntegerField(primary_key=True)
    day = models.DateField()
    clip_id = models.BigIntegerField(blank=True, null=True)
    is_rtsp = models.BooleanField()
    is_itunes = models.BooleanField()
    collection_id = models.BigIntegerField(blank=True, null=True)
    instid = models.TextField(blank=True, null=True)
    format = models.TextField(blank=True, null=True)
    quality = models.TextField(blank=True, null=True)
    fetch_type = models.TextField(blank=True, null=True)
    is_cam = models.BooleanField()
    country = models.TextField(blank=True, null=True)
    num_hits = models.BigIntegerField()
    num_bytes = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'media_stats_by_day'
