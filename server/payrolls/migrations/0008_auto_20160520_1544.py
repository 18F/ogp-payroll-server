# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-20 15:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payrolls', '0007_auto_20160519_1703'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withholding',
            name='worker',
        ),
        migrations.AddField(
            model_name='withholding',
            name='workweek',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='payrolls.Workweek'),
            preserve_default=False,
        ),
    ]
