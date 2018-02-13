
from django.core.management import BaseCommand
from rest_framework.reverse import reverse

from tests.test_api import CREATE_POSTER_FIELDS

import requests


class Command(BaseCommand):

    SERVER = 'http://localhost:8000'
    help = ("Adds some posters into the database for user testing. `make loaddata` must have been called beforehand "
            "and development server must be running on {server}.".format(server=SERVER))

    def add_arguments(self, parser):
        parser.add_argument('N', nargs='?', type=int, default=5, help="number of posters")

    def handle(self, *args, **options):
        for i in range(options['N']):
            requests.post("{server}{url}".format(server=self.SERVER, url=reverse('poster-list')),
                          json={
                             'bureau': 1,
                             'spec': 1,
                             'fields': CREATE_POSTER_FIELDS,
                          })
