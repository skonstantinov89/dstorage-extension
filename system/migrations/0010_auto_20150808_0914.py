# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0009_auto_20150729_2327'),
    ]

    operations = [
        migrations.AddField(
            model_name='criterion',
            name='field10',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field11',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field12',
            field=models.TextField(blank=True, null=True),
        ),
    ]
