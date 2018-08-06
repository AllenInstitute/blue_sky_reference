# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-03 19:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blue_sky', '0002_observation_proc_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Calibration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offset', models.IntegerField(null=True)),
                ('proc_state', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ObservationGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255, null=True)),
                ('group_state', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='groupassignment',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blue_sky.ObservationGroup'),
        ),
        migrations.AddField(
            model_name='groupassignment',
            name='observation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blue_sky.Observation'),
        ),
        migrations.AddField(
            model_name='observation',
            name='groups',
            field=models.ManyToManyField(related_name='observations', through='blue_sky.GroupAssignment', to='blue_sky.ObservationGroup'),
        ),
    ]
