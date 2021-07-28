import csv
from django.core.management.base import BaseCommand

from hasworn.wearers.models import Wearer
from hasworn.clothing.models import Clothing, Wearing, Worn


class Command(BaseCommand):
    help = 'Generate the wearer site'

    def add_arguments(self, parser):
        parser.add_argument('wearer')

    def handle(self, *args, **options):
        wearer = Wearer.objects.get(username=options['wearer'])
        wearer.generate_wearer_site()
