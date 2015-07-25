# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20150725_1226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='archiveStartDate',
            field=models.DateField(null=True, blank=True),
        ),
    ]
