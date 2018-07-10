from django.db import models


class Video(models.Model):
    """
    A JWPlatform video resource.

    """
    #: JWPlatform video key
    key = models.CharField(primary_key=True, max_length=64, editable=False)

    #: Corresponding :py:class:`mediaplatform.MediaItem`. Accessible from the
    #: :py:class:`mediaplatform.MediaItem` model via the ``jwp`` field.
    item = models.OneToOneField('mediaplatform.MediaItem', related_name='jwp',
                                on_delete=models.CASCADE)

    #: The updated timestamp from JWPlatform. Used to determine which items need updating.
    updated = models.BigIntegerField(help_text='Last updated timestamp')
