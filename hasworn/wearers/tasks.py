from celery import shared_task
from datetime import datetime

from .models import Wearer


@shared_task
def rebuild_full_wearer_site(wearer_pk, previous_update=None):
    wearer = Wearer.objects.get(pk=wearer_pk)
    if previous_update and previous_update == wearer.get_last_update():
        wearer.generate_wearer_site()


@shared_task
def quick_rebuild_of_worn(wearer_pk, worn, year):
    wearer = Wearer.objects.get(pk=wearer_pk)
    wearer.generate_wearer_site_worn(worn, year)
