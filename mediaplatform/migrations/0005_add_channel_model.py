# Generated by Django 2.0.7 on 2018-07-31 09:07

from django.db import migrations, models
import django.db.models.deletion
import mediaplatform.models


class Migration(migrations.Migration):

    dependencies = [
        ('mediaplatform', '0004_uploadendpoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.CharField(default=mediaplatform.models._make_token, editable=False, max_length=11, primary_key=True, serialize=False)),
                ('title', models.TextField(help_text='Title of media item')),
                ('description', models.TextField(blank=True, default='', help_text='Description of media item')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='permission',
            name='allows_edit_channel',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edit_permission', to='mediaplatform.Channel'),
        ),
    ]
