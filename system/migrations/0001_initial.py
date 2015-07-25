# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('criteriaType', models.TextField()),
                ('criteriaValue', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('active', models.BooleanField(default=True)),
                ('status', models.TextField()),
                ('location', models.TextField()),
                ('officeStartDate', models.DateField()),
                ('centralManagementStartDate', models.DateField()),
                ('archiveStartDate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('requestDate', models.DateField()),
                ('status', models.TextField()),
                ('fromLocation', models.TextField()),
                ('toLocation', models.TextField()),
                ('protocolID', models.IntegerField()),
                ('documentID', models.ForeignKey(to='system.Document')),
                ('userID', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='criterion',
            name='documentID',
            field=models.ForeignKey(to='system.Document'),
        ),
    ]
