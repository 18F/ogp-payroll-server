# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-18 18:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('wage_determinations', '0001_initial'), ]

    operations = [
        migrations.AddField(model_name='rate',
                            name='survey_location_qualifier',
                            field=models.TextField(blank=True), ),
    ]
