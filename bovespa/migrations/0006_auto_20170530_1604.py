# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bovespa', '0005_auto_20170530_1600'),
    ]

    operations = [
        migrations.AlterField(
            model_name='financialreport',
            name='url',
            field=models.TextField(),
        ),
    ]
