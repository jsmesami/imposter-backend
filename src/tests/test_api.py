import base64
import datetime
from copy import deepcopy
import os
import shutil

import factory

from django.conf import settings
from django.core.management import call_command
from django.test import override_settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from imposter.models.image import PosterImage
from imposter.models.poster import Poster
from utils.functional import deepmerge


with open(os.path.join(settings.BASE_DIR, 'tests/data/small_image.jpg'), 'rb') as image_file:
    SMALL_IMAGE = str(base64.b64encode(image_file.read()), encoding='ascii')


CREATE_POSTER_FIELDS = {
    'title': {
        'text': 'Testovací poster',
    },
    'main_image': {
        'filename': 'main.jpeg',
        'data': SMALL_IMAGE,
    },
    'event_price': {
        'text': 'Vstup volný',
    },
    'event_date': {
        'text': 'Pondělí, 28. února, od 19 do 21 h',
    },
    'summary': {
        'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore '
                'et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi '
                'ut aliquip ex ea commodo consequat.',
    },
    'bureau_address': {
        'text': 'Mariánské náměstí 98/1, Praha 1',
    },
    'partner_logo_1': {
        'filename': 'logo1.jpeg',
        'data': SMALL_IMAGE,
    },
}

UPDATE_POSTER_FIELDS = {
    'summary': {
        'text': 'Toto shrnutí bylo upraveno',
    },
    'partner_logo_1': {
        'filename': 'logo1_replaced.jpeg',
        'data': SMALL_IMAGE,
    },
    'partner_logo_2': {
        'filename': 'logo2_added.jpeg',
        'data': SMALL_IMAGE,
    },
}

TOMORROW = datetime.datetime.today() + datetime.timedelta(days=1)
MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'tests/media')


class PosterFactory(factory.DjangoModelFactory):

    class Meta:
        model = Poster

    spec_id = 1
    bureau_id = 1
    saved_fields = CREATE_POSTER_FIELDS


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class TestApi(APITestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('loaddata', os.path.join(settings.BASE_DIR, 'fixtures/bureau.json'))
        call_command('load_specs')
        cls.poster = PosterFactory()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT)  # Clean up test media
        super().tearDownClass()

    def check_images(self, fields):
        images_lookup = {f['id']: f['url'] for f in fields.values() if f['type'] == 'image'}
        images_qs = PosterImage.objects.filter(id__in=images_lookup.keys())

        for i in images_qs.iterator():
            self.assertEqual(i.file.url, images_lookup[i.pk])  # file url == field url

        for path in (i.file.path for i in images_qs.iterator()):
            self.assertTrue(os.path.isfile(path) and os.path.getsize(path))  # file exists and size > 0

    def check_texts(self, in_fields, out_fields):
        def get_texts(fields):
            return sorted(filter(None, (f.get('text') for f in fields.values())))

        self.assertEqual(get_texts(in_fields), get_texts(out_fields))

    def check_poster_files(self, data):
        poster = Poster.objects.get(pk=data['id'])
        self.assertEqual(data['thumb'], poster.thumb.url)
        self.assertTrue(os.path.isfile(poster.thumb.path) and os.path.getsize(poster.thumb.path))
        self.assertEqual(data['print'], poster.print.url)
        self.assertTrue(os.path.isfile(poster.print.path) and os.path.getsize(poster.print.path))

    def create_poster(self, fields):
        return self.client.post(reverse('poster-list'), data=dict(bureau=1, spec=1, fields=fields))

    def read_poster(self, pk):
        return self.client.get(reverse('poster-detail', args=[pk]))

    def update_poster(self, pk, fields):
        return self.client.patch(reverse('poster-detail', args=[pk]), data=dict(fields=fields))

    def delete_poster(self, pk):
        return self.client.delete(reverse('poster-detail', args=[pk]))

    # Test resources listing

    def test_resources_listing_success(self):
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_bureau_listing_success(self):
        response = self.client.get(reverse('bureau-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_spec_listing_success(self):
        response = self.client.get(reverse('posterspec-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poster_listing_success(self):
        response = self.client.get(reverse('poster-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poster_listing_with_filter_success(self):
        query = '?bureau=1&spec=1&limit=1&offset=0&since={since}&until={until}'.format(
            since=datetime.datetime.now() - datetime.timedelta(days=1),
            until=datetime.datetime.now() + datetime.timedelta(days=1),
        )
        response = self.client.get(reverse('poster-list') + query)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_poster_listing_fails_with_wrong_filter(self):
        query = '?bureau=x&spec=x&since=x&until=x'
        response = self.client.get(reverse('poster-list') + query)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['filters'], [
            "Invalid date format of 'since': x",
            "Invalid date format of 'until': x",
            "Invalid 'bureau' ID: x",
            "Invalid 'spec' ID: x",
        ])

    # Test poster CREATE

    def test_poster_create_success(self):
        response = self.create_poster(CREATE_POSTER_FIELDS)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        fields = response.data['fields']
        self.check_images(fields)
        self.check_texts(CREATE_POSTER_FIELDS, fields)
        self.check_poster_files(response.data)

    def test_poster_create_fails_with_disallowed_fields(self):
        disallowed_fields = {
            'a': {},
            'b': {},
        }
        response = self.create_poster(deepmerge(disallowed_fields, deepcopy(CREATE_POSTER_FIELDS)))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ['Fields not allowed: a, b'])

    def test_poster_create_fails_with_missing_required_fields(self):
        fields = deepcopy(CREATE_POSTER_FIELDS)
        del fields['title']
        response = self.create_poster(fields)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ['Missing required fields: title'])

    def test_poster_create_fails_with_disallowed_field_parameters(self):
        disallowed_field_params = {
            'title': {
                'c': '',
                'd': '',
            }
        }
        response = self.create_poster(deepmerge(disallowed_field_params, deepcopy(CREATE_POSTER_FIELDS)))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ["Parameters not allowed for text field 'title': c, d"])

    def test_poster_create_fails_with_missing_required_parameters(self):
        fields = deepcopy(CREATE_POSTER_FIELDS)
        del fields['title']['text']
        response = self.create_poster(fields)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ["Missing required parameters for text field 'title': text"])

    # Test poster READ

    def test_poster_read_success(self):
        response = self.read_poster(self.poster.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = response.data['fields']
        self.check_images(fields)
        self.check_texts(CREATE_POSTER_FIELDS, fields)
        self.check_poster_files(response.data)

    # Test poster UPDATE

    def test_poster_update_success(self):
        response = self.update_poster(self.poster.pk, UPDATE_POSTER_FIELDS)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        fields = response.data['fields']
        self.check_images(fields)
        self.check_texts(deepmerge(UPDATE_POSTER_FIELDS, CREATE_POSTER_FIELDS), fields)
        self.check_poster_files(response.data)

    def test_poster_update_fails_for_corrupted_image_data(self):
        corrupted_image = {
            'main_image': {
                'filename': 'main.jpg',
                'data': 'gibberish',
            },
        }
        response = self.update_poster(self.poster.pk, corrupted_image)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ["Incorrect image. Can't decode image data: main.jpg"])

    def test_poster_update_fails_for_unsupported_image_extension(self):
        unsupported_extension = {
            'main_image': {
                'filename': 'main.pdf',
                'data': SMALL_IMAGE,
            },
        }
        response = self.update_poster(self.poster.pk, unsupported_extension)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ['Incorrect image. Unsupported image file extension: main.pdf'])

    def test_poster_update_fails_for_too_large_image(self):
        exceeded_image_size = {
            'main_image': {
                'filename': 'main.jpg',
                'data': '*' * (settings.UPLOADED_FILE_MAX_SIZE + 1),
            },
        }
        response = self.update_poster(self.poster.pk, exceeded_image_size)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['fields'], ['Incorrect image. Image exceeds maximum file size: main.jpg'])

    # Test poster DELETE

    def test_poster_delete_success(self):
        response = self.delete_poster(self.poster.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Successfully deleted.')
