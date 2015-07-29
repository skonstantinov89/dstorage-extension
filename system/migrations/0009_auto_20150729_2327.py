# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system', '0008_auto_20150729_2257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='protocols',
            name='requestID',
        ),
        migrations.RemoveField(
            model_name='requests',
            name='fromLocation',
        ),
        migrations.RemoveField(
            model_name='requests',
            name='requestDate',
        ),
        migrations.RemoveField(
            model_name='requests',
            name='toLocation',
        ),
        migrations.RemoveField(
            model_name='requests',
            name='userID',
        ),
        migrations.AddField(
            model_name='protocols',
            name='fromLocation',
            field=models.TextField(default='storage 1'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='protocols',
            name='requestDate',
            field=models.DateField(default=datetime.datetime(2015, 7, 29, 23, 26, 28, 943701)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='protocols',
            name='toLocation',
            field=models.TextField(default='storage 2'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='protocols',
            name='userID',
            field=models.ForeignKey(default='', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requests',
            name='protocolID',
            field=models.ForeignKey(default='', to='system.Protocols'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requests',
            name='verifierID',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
    ]
