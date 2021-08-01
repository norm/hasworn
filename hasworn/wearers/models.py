from datetime import date, timedelta
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .pages import WearerPage, WearerWornPage, WearerYear, WearerTypeIndex, WearerCSV


class Wearer(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length = 30,
        unique = True,
        help_text = _(
            'Required. 30 characters or less. '
            'Letters, digits, and hyphens only.'
        ),
        validators=[
            validators.RegexValidator(
                r'^[a-z][a-z0-9-]+$',
                _(
                    'Enter a valid username. '
                     'The username must start with a letter, '
                     'and may contain only letters, numbers and hyphens.'
                ),
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    # names are more complex than first/last so don't even try
    first_name = None
    last_name = None
    name = models.CharField(
        _('name'), 
        max_length = 1024,
        blank = True,
        null = True,
    )

    USERNAME_FIELD = 'username'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.username

    def get_name(self):
        if not self.name:
            return self.username
        else:
            return self.name

    @property
    def wearing_today(self):
        return self.wearings.filter(day=date.today())

    @property
    def worn_previously(self):
        return self.wearings.filter(day__lt=date.today())

    @property
    def wearings(self):
        from hasworn.clothing.models import Wearing
        return Wearing.objects.filter(worn__wearer=self)

    def most_worn(self):
        # FIXME also order by date first worn
        return self.worn_set.annotate(
                num_worn = models.Count('days_worn')
            ).order_by('-num_worn')

    def most_worn_recently(self, cut_off=None):
        if not cut_off:
            cut_off = date.today() - timedelta(days=180)
        # FIXME also order by date first worn
        return self.worn_set.filter(
                days_worn__day__gte = cut_off
            ).annotate(
                num_worn=models.Count('days_worn')
            ).filter(
                num_worn__gt = 1
            ).order_by('-num_worn')

    def years_active(self):
        return [ year.year for year in self.wearings.dates('day', 'year') ]

    def generate_wearer_site_wearing(self, wearing):
        WearerWornPage(wearer=self, pk=wearing.worn.pk).create()
        WearerTypeIndex(wearer=self).create()
        WearerYear(wearer=self, year=wearing.day.year).create()
        WearerPage(wearer=self).create()
        WearerCSV(wearer=self).create()

    def generate_wearer_site(self):
        WearerPage(wearer=self).create()
        for worn in self.has_worn.all():
            WearerWornPage(wearer=self, pk=worn.pk).create()
        for year in self.years_active():
            WearerYear(wearer=self, year=year).create()
        WearerTypeIndex(wearer=self).create()
        WearerCSV(wearer=self).create()
