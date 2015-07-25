# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='userID',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='document',
            name='archiveStartDate',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='centralManagementStartDate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='officeStartDate',
            field=models.DateField(null=True, blank=True),
        ),
    ]
