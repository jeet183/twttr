# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2019-11-04 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='interest',
            field=models.TextField(blank=True, null=True),
        ),
    ]
