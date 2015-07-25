# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='fileID',
            field=models.ForeignKey(default=-1, to='system.Files'),
            preserve_default=False,
        ),
    ]
