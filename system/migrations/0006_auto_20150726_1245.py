# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_document_fileid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='fileID',
            field=models.ForeignKey(blank=True, to='system.Files', null=True),
        ),
    ]
