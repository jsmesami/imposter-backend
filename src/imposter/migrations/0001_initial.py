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
                ('number', models.PositiveSmallIntegerField()),
                ('address', models.CharField(max_length=255)),
                ('disabled', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Poster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
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
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file', models.ImageField(upload_to=imposter.models.image.Image._upload_to)),
                ('poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='imposter.Poster')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PosterSpec',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
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
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', utils.fields.AutoDateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('file', models.ImageField(upload_to=imposter.models.image.Image._upload_to)),
                ('spec', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='imposter.PosterSpec')),
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
