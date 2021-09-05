import csv
from django.core.management.base import BaseCommand

from hasworn.wearers.tasks import rebuild_all_wearer_sites


class Command(BaseCommand):
    help = 'Generate all wearer sites'

    def handle(self, *args, **options):
        rebuild_all_wearer_sites()
