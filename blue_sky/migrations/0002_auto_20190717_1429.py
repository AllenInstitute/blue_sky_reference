# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-07-17 21:29
from __future__ import unicode_literals

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('blue_sky', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observationgroup',
            name='object_state',
            field=django_fsm.FSMField(default='PENDING', max_length=50),
        ),
    ]