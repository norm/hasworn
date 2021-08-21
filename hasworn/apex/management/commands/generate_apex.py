import csv
from django.core.management.base import BaseCommand

from hasworn.apex.pages import ApexPage


class Command(BaseCommand):
    help = 'Generate the apex site'

    def handle(self, *args, **options):
        ApexPage().create()
