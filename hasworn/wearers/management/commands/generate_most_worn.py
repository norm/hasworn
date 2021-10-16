import csv
from django.core.management.base import BaseCommand

from hasworn.wearers.models import Wearer
from hasworn.clothing.models import Clothing, Wearing, Worn
from hasworn.wearers.pages import WearerMostWornFragment


class Command(BaseCommand):
    help = 'Generate the most_worn fragment'

    def add_arguments(self, parser):
        parser.add_argument('wearer')
        parser.add_argument('date')

    def handle(self, *args, **options):
        wearer = Wearer.objects.get(username=options['wearer'])
        WearerMostWornFragment(wearer=wearer, date=options['date']).create()
