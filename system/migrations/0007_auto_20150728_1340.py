# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_auto_20150726_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='criterion',
            name='criteriaType',
        ),
        migrations.RemoveField(
            model_name='criterion',
            name='criteriaValue',
        ),
        migrations.AddField(
            model_name='criterion',
            name='field1',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field2',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field3',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field4',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field5',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field6',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field7',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field8',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='criterion',
            name='field9',
            field=models.TextField(blank=True, null=True),
        ),
    ]
