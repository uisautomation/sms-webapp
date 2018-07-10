from django.db import models


class MediaItem(models.Model):
    #: SMS media id
    id = models.BigIntegerField(primary_key=True, editable=False, help_text='Legacy SMS media id')

    #: Corresponding :py:class:`mediaplatform.MediaItem`. Accessible from the
    #: :py:class:`mediaplatform.MediaItem` model via the ``sms`` field.
    item = models.OneToOneField('mediaplatform.MediaItem', related_name='sms',
                                on_delete=models.CASCADE)

    #: The last updated at time from the legacy SMS. Used to determine which items need updating.
    last_updated_at = models.DateTimeField(help_text='Last updated at time from SMS')


class Collection(models.Model):
    #: SMS collection id
    id = models.BigIntegerField(primary_key=True, editable=False,
                                help_text='Legacy SMS collection id')

    #: Corresponding :py:class:`mediaplatform.Collection`. Accessible from the
    #: :py:class:`mediaplatform.Collection` model via the ``sms`` field.
    item = models.OneToOneField('mediaplatform.Collection', related_name='sms',
                                on_delete=models.CASCADE)

    #: The last updated at time from the legacy SMS. Used to determine which collections need
    #: updating.
    last_updated_at = models.DateTimeField(help_text='Last updated at time from SMS')
