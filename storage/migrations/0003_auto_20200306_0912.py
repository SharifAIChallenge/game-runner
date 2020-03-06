# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-03-06 09:12
from __future__ import unicode_literals

from django.db import migrations, models
import storage.models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_auto_20170209_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(upload_to=storage.models.get_file_path),
        ),
    ]