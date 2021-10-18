from datetime import date, timedelta
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

from .pages import (
    WearerPage,
    WearerWornPage,
    WearerYear,
    WearerTypeIndex,
    WearerMostRecentlyWorn,
    WearerMostFrequentlyWorn,
    WearerFirstWorn,
    WearerCSV,
    WearerAtom,
    WearerCalendar,
    WearerNotFoundPage,
)

FIVE_MINUTES = ( 60 * 5 )


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
    last_update = models.DateTimeField(
        auto_now = True,
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

        return Wearing.objects.filter(
                worn__wearer=self
            ).order_by('-day', 'worn__clothing__name')

    @property
    def wearings_by_first_worn(self):
        from hasworn.clothing.models import Wearing

        first_day = Wearing.objects.filter(
                worn = models.OuterRef('pk'),
            ).order_by('day')

        return self.worn_set.annotate(
                first_day = models.Subquery(first_day.values('day')[:1]),
            ).order_by('-first_day', 'clothing__name')

    def most_worn(self):
        from hasworn.clothing.models import Wearing

        last_day = Wearing.objects.filter(
                worn = models.OuterRef('pk')
            ).order_by('-day')

        return self.worn_set.annotate(
                num_worn = models.Count('days_worn'),
                last_day = models.Subquery(last_day.values('day')[:1]),
            ).order_by('-num_worn', 'last_day', 'pk')

    def most_worn_recently(self, cut_off=None):
        from hasworn.clothing.models import Wearing

        last_day = Wearing.objects.filter(
                worn = models.OuterRef('pk')
            ).order_by('-day')
        if not cut_off:
            cut_off = date.today() - timedelta(days=180)

        return self.worn_set.filter(
                days_worn__day__gte = cut_off
            ).annotate(
                num_worn = models.Count('days_worn'),
                last_day = models.Subquery(last_day.values('day')[:1]),
            ).filter(
                num_worn__gt = 1
            ).order_by('-num_worn', 'last_day', 'pk')

    def most_worn_at(self, date):
        from hasworn.clothing.models import Wearing

        last_day = Wearing.objects.filter(
                day__lte = date,
                worn = models.OuterRef('pk'),
            ).order_by('-day')

        return self.worn_set.filter(
                days_worn__day__lte = date
            ).annotate(
                num_worn = models.Count('days_worn'),
                last_day = models.Subquery(last_day.values('day')[:1]),
            ).order_by('-num_worn', 'last_day', 'pk')

    def most_worn_average(self):
        return sorted(
                self.worn_set.all(),
                key=lambda worn: 
                    '%05d-%05d' % (
                        worn.average_days_between_wearings,
                        worn.last_worn_days,
                    )
            )

    def years_active(self):
        return [ year.year for year in self.wearings.dates('day', 'year') ]

    def get_last_update(self):
        """ last_update in a form for comparison after JSON serialization """
        return str(self.last_update.replace(microsecond=0))

    def added_wearing(self, wearing):
        self.update_site_from_wearing(wearing.worn.pk, wearing.day.year)

    def deleted_wearing(self, worn, year):
        self.update_site_from_wearing(worn, year)

    def update_site_from_wearing(self, worn, year):
        from .tasks import (
            rebuild_full_wearer_site,
            quick_rebuild_of_worn,
        )

        self.register_update()
        quick_rebuild_of_worn.delay(self.pk, worn, year)
        rebuild_full_wearer_site.apply_async(
            args = [self.pk, self.get_last_update()],
            countdown = FIVE_MINUTES,
        )

    def register_update(self):
        # last_update is auto, just save self
        self.save()

    def generate_wearer_site(self):
        for worn in self.has_worn.all():
            WearerWornPage(wearer=self, pk=worn.pk).create()
        for year in self.years_active():
            WearerYear(wearer=self, year=year).create()
        WearerTypeIndex(wearer=self).create()
        WearerMostRecentlyWorn(wearer=self).create()
        WearerMostFrequentlyWorn(wearer=self).create()
        WearerFirstWorn(wearer=self).create()
        WearerCSV(wearer=self).create()
        WearerAtom(wearer=self).create()
        WearerCalendar(wearer=self).create()
        WearerPage(wearer=self).create()
        WearerNotFoundPage(wearer=self).create()

    def generate_wearer_site_worn(self, worn_pk, year):
        WearerWornPage(wearer=self, pk=worn_pk).create()
        WearerYear(wearer=self, year=year).create()
        WearerPage(wearer=self).create()
