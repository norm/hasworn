import csv
from datetime import date
from django.core.management.base import BaseCommand

from hasworn.wearers.models import Wearer
from hasworn.clothing.models import Clothing, Wearing, Worn


class Command(BaseCommand):
    help = 'Import wearings from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file')

    def handle(self, *args, **options):
        with open(options['csv_file']) as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                print(row)
                wearer = Wearer.objects.get(username = row['wearer'])
                clothing, _ = Clothing.objects.get_or_create(
                    name = row['name'],
                    slug = row['slug'],
                    type = row['type'],
                    created_by = wearer,
                )
                worn, _ = Worn.objects.get_or_create(
                    clothing = clothing,
                    wearer = wearer,
                )
                wearing = Wearing.objects.get_or_create(
                    worn = worn,
                    day = date.fromisoformat(row['day']),
                )
