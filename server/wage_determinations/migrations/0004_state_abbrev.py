# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('wage_determinations', '0003_rate_fts_index'), ]

    operations = [
        migrations.AddField(model_name='state',
                            name='abbrev',
                            field=models.TextField(default='OH',
                                                   unique=True),
                            preserve_default=False, ),
    ]
