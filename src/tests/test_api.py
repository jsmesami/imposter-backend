import os

import factory

from django.conf import settings
from django.core.management import call_command

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from imposter.models.image import PosterImage
from imposter.models.poster import Poster, walk_fields

CREATE_POSTER_FIELDS = {
    'title': {
        'text': 'title'
    },
    'main_image':  {
        'filename': 'main.gif',
        'data': 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
    },
    'event_price': {
        'text': 'price'
    },
    'event_date': {
        'text': 'date'
    },
    'summary': {
        'text': 'summary'
    },
    'bureau_address': {
        'text': 'address'
    },
    'partner_logos': {
        'fields': {
            'logo1': {
                'filename': 'logo1.gif',
                'data': 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            },
            'logo2': {
                'filename': 'logo2.gif',
                'data': 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            }
        }
    }
}

UPDATE_POSTER_FIELDS = {
    'summary': {
        'text': 'updated',
    },
}


class PosterFactory(factory.DjangoModelFactory):

    class Meta:
        model = Poster

    spec_id = 1
    bureau_id = 1
    saved_fields = CREATE_POSTER_FIELDS


class TestApi(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', os.path.join(settings.BASE_DIR, 'fixtures/bureau.json'))
        call_command('load_specs')
        cls.poster = PosterFactory()

    def check_images_count(self, fields):
        image_ids = list(filter(None, [i.get('id') for i in walk_fields(fields)]))
        images = PosterImage.objects.filter(id__in=image_ids)
        self.assertEqual(len(image_ids), images.count())

    def check_texts(self, fields):
        for field, value in CREATE_POSTER_FIELDS.items():
            self.assertEqual(fields[field].get('text'), value.get('text'))

    def test_spec(self):
        response = self.client.get(reverse('posterspec-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poster_create(self):
        response = self.client.post(reverse('poster-list'), data=dict(
            bureau=1,
            spec=1,
            fields=CREATE_POSTER_FIELDS,
        ))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        fields = dict(response.data)['fields']
        self.check_images_count(fields)
        self.check_texts(fields)

    def test_poster_read(self):
        response = self.client.get(reverse('poster-detail', args=[self.poster.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = dict(response.data)['fields']
        self.check_images_count(fields)
        self.check_texts(fields)

    def test_poster_update(self):
        response = self.client.patch(reverse('poster-detail', args=[self.poster.pk]), data=dict(
            fields=UPDATE_POSTER_FIELDS,
        ))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = dict(response.data)['fields']
        self.assertEqual(fields['summary']['text'], UPDATE_POSTER_FIELDS['summary']['text'])
