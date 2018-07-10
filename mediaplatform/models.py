import uuid

from django.db import models
import django.contrib.postgres.fields as pgfields


class Permission(models.Model):
    """
    Specify whether a user has permission to perform some action.

    A user has permission to perform the action if *any* of the following are true:

    * They have a crsid and that crsid appears in :py:attr:`~.crsids`
    * The numeric id of a lookup group which they are a member of appears in
      :py:attr:`~.lookup_groups`
    * The instid of an an institution they are a member of appears in
      :py:attr:`~.lookup_insts`
    * The :py:attr:`~.is_public` flag is ``True``
    * The user is not anonymous and :py:attr:`is_signed_in` is ``True``

    """
    #: Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: List of crsids of users with this permission
    crsids = pgfields.ArrayField(models.TextField(), blank=True, default=[])

    #: List of lookup groups which users with this permission belong to
    lookup_groups = pgfields.ArrayField(models.BigIntegerField(), blank=True, default=[])

    #: List of lookup institutions which users with this permission belong to
    lookup_insts = pgfields.ArrayField(models.TextField(), blank=True, default=[])

    #: Do all users (including anonymous ones) have this permission?
    is_public = models.BooleanField(default=False)

    #: Do all signed in (non-anonymous) users have this permission?
    is_signed_in = models.BooleanField(default=False)


class MediaItem(models.Model):
    """
    An individual media item in the media platform.

    """
    #: Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: Media item title
    title = models.TextField(help_text='Title of media item')

    #: Media item description
    description = models.TextField(blank=True, help_text='Description of media item')

    downloadable = models.BooleanField(
        help_text='If this item can be viewed, can it also be downloaded?')

    # We use on_delete=models.PROTECT here to make sure that the referenced permission cannot be
    # deleted from under our feet. We set the related name to "+" to stop Django trying to create a
    # related field back from the Permission object. If it tried to do so there would be a sea of
    # "allows_view_on_media_item"-like fields on Permission which would clutter things immensely.

    #: :py:class:`~.Permission` determining who can view this item
    view_permission = models.OneToOneField(Permission, on_delete=models.PROTECT,
                                           help_text='Restriction on who can see/hear this item',
                                           related_name='+')

    #: :py:class:`~.Permission` determining who can edit this item
    edit_permission = models.OneToOneField(Permission, on_delete=models.PROTECT,
                                           help_text='Restriction on who can modify this item',
                                           related_name='+')

    # We use max_length=10 here to future proof us against the day when we inevitably have our
    # first "length 4 three-letter code". :)

    #: ISO 693-3 language code
    language = models.CharField(
        max_length=10,
        help_text=(
            'ISO 639-3 three letter language code describing majority language used in this item'
        )
    )

    #: Video copyright
    copyright = models.TextField(blank=True, help_text='Free text describing Copyright holder')

    #: List of tags for video
    tags = pgfields.ArrayField(models.CharField(max_length=256), blank=True,
                               help_text='Tags/keywords for item')

    #: Creation time
    created_at = models.DateTimeField(auto_now_add=True)

    #: Last update time
    updated_at = models.DateTimeField(auto_now=True)

    #: Deletion time. If non-NULL, the item has been "deleted" and should not usually be visible.
    deleted_at = models.DateTimeField(null=True, blank=True)


class Collection(models.Model):
    """
    A collection of media items.

    """
    #: Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: Collection title
    title = models.TextField(help_text='Title of collection')

    #: Collection description
    description = models.TextField(help_text='Description for collection')

    #: :py:class:`~.MediaItem` objects which make up this collection. Postgres does not (currently)
    #: allow array elements to have a foreign key constraint added to them so we need to represent
    #: the links as bare UUIDs. The upshot of this is that code which uses this field needs to
    #: handle the (rare) case that a UUID in the list does not correspond to a current video.
    #: YouTube, as an example, has this problem as well since videos in playlists are sometimes
    #: replaced by a "deleted video" placeholder.
    media_items = pgfields.ArrayField(
        models.UUIDField(), blank=True, help_text='Primary keys of media items in this collection')

    # We use on_delete=models.PROTECT here to make sure that the referenced permission cannot be
    # deleted from under our feet. We set the related name to "+" to stop Django trying to create a
    # related field back from the Permission object. If it tried to do so there would be a sea of
    # "allows_view_on_media_item"-like fields on Permission which would clutter things immensely.

    #: :py:class:`~.Permission` determining who can view this item
    view_permission = models.OneToOneField(
        Permission, on_delete=models.PROTECT, related_name='+',
        help_text='Restriction on who can see which items are in this collection')

    #: :py:class:`~.Permission` determining who can edit this item
    edit_permission = models.OneToOneField(
        Permission, on_delete=models.PROTECT, related_name='+',
        help_text='Restriction on who can modify this collection')

    #: Creation time
    created_at = models.DateTimeField(auto_now_add=True)

    #: Last update time
    updated_at = models.DateTimeField(auto_now=True)

    #: Deletion time. If non-NULL, the item has been "deleted" and should not usually be visible.
    deleted_at = models.DateTimeField(null=True, blank=True)
