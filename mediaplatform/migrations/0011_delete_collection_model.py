# Generated by Django 2.1 on 2018-08-07 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mediaplatform', '0010_alter_playlist_media_items_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='permission',
            name='allows_edit_collection',
        ),
        migrations.RemoveField(
            model_name='permission',
            name='allows_view_collection',
        ),
        migrations.DeleteModel(
            name='Collection',
        ),
    ]
