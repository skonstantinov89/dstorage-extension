# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_auto_20150728_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='Protocols',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='requests',
            name='protocolID',
        ),
        migrations.AddField(
            model_name='protocols',
            name='requestID',
            field=models.ForeignKey(to='system.Requests'),
        ),
    ]
