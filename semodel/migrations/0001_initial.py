# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-02 03:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('intext', models.CharField(default='', max_length=500)),
            ],
        ),
    ]