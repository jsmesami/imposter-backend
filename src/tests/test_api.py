import os

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient


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
            }
        }
    }
}


class TestApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        call_command('loaddata', os.path.join(settings.BASE_DIR, 'fixtures/bureau.json'))
        call_command('load_specs')

    def testSpec(self):
        response = self.client.get(reverse('posterspec-list'))
        self.assertEqual(response.status_code, 200)

    def testPosterCreation(self):
        response = self.client.post(reverse('poster-list'), data=dict(
            bureau=1,
            spec=1,
            fields=CREATE_POSTER_FIELDS,
        ))
        self.assertEqual(response.status_code, 201)

        response = self.client.get(reverse('poster-detail', args=[1]))
        self.assertEqual(response.status_code, 200)
