# Generated by Django 2.0 on 2017-12-29 12:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone
import imposter.models.image
import imposter.models.poster
import utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bureau',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('abbrev', models.CharField(max_length=8)),
                ('address', models.CharField(max_length=255)),
                ('disabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('saved_fields', django.contrib.postgres.fields.jsonb.JSONField(editable=False)),
                ('thumb', models.ImageField(editable=False, upload_to=imposter.models.poster.Poster._upload_to)),
                ('print', models.FileField(editable=False, upload_to=imposter.models.poster.Poster._upload_to)),
                ('bureau', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posters', to='imposter.Bureau')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PosterImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('file', models.ImageField(upload_to=imposter.models.image.Image._upload_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PosterSpec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('w', models.PositiveIntegerField()),
                ('h', models.PositiveIntegerField()),
                ('color', models.CharField(max_length=6)),
                ('thumb', models.ImageField(upload_to='specs/thumbs')),
                ('frames', django.contrib.postgres.fields.jsonb.JSONField()),
                ('fields', django.contrib.postgres.fields.jsonb.JSONField()),
                ('disabled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpecImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False)),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False)),
                ('file', models.ImageField(upload_to=imposter.models.image.Image._upload_to)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='poster',
            name='spec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posters', to='imposter.PosterSpec'),
        ),
    ]
