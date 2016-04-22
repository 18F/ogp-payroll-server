# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-19 14:38
from __future__ import unicode_literals

from django.db import migrations
import pg_fts.fields
from pg_fts.migrations import CreateFTSIndexOperation, CreateFTSTriggerOperation


class Migration(migrations.Migration):

    dependencies = [
        ('wage_determinations', '0002_rate_survey_location_qualifier'),
    ]

    operations = [
        migrations.AddField(
            model_name='rate',
            name='fts_index',
            field=pg_fts.fields.TSVectorField(default='', dictionary='portuguese', editable=False, fields=(('occupation', 'A'), ('rate_name', 'B'), ('subrate_name', 'B'), 'occupation_qualifier', 'rate_name_qualifier', 'subrate_name_qualifier'), null=True, serialize=False),
        ),
        CreateFTSIndexOperation(
            name='Rate',
            fts_vector='fts_index',
            index='gin'
        ),
        CreateFTSTriggerOperation(
        name='Rate',
        fts_vector='fts_index',
        ),
    ]