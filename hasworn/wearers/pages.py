import csv
from datetime import date
from django.conf import settings
from hasworn.pages import ModelPage, StaticPage, FeedPage, CalendarPage
import os


class WearerPage(StaticPage):
    template = 'wearers/wearer_page.html'


class WearerWornPage(ModelPage):
    template = 'wearers/wearer_worn_page.html'

    def get_model(self):
        from hasworn.clothing.models import Worn
        return Worn

    def get_filename(self):
        return "%s/tshirts/%s.html" % (self.wearer.username, self.object.clothing.slug)


class WearerYear(StaticPage):
    template = 'wearers/wearer_year.html'

    def get_filename(self):
        return "%s/%s/index.html" % (self.wearer.username, self.year)

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context['year'] = self.year
        context['wearings'] = self.wearer.wearings.select_related(
                'worn__clothing'
            ).filter(
                day__gte=date(self.year, 1, 1),
                day__lte=date(self.year, 12, 31)
            ).order_by('day')
        context['distinct_wearings'] = set()
        context['new_wearings'] = set()
        for wearing in context['wearings']:
            context['distinct_wearings'].add(wearing.worn.pk)
            this_year = (
                    wearing.worn.first_worn.day >= date(self.year, 1, 1)
                    and
                    wearing.worn.first_worn.day <= date(self.year, 12, 31)
                )
            if this_year:
                context['new_wearings'].add(wearing.worn.pk)
        return context


class WearerTypeIndex(StaticPage):
    template = 'wearers/wearer_type_index.html'

    def get_filename(self):
        return "%s/%s/index.html" % (self.wearer.username, 'tshirts')

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context['sort_by'] = 'often'
        context['wearings'] = self.wearer.most_worn()
        return context


class WearerMostRecentlyWorn(StaticPage):
    template = 'wearers/wearer_type_index.html'

    def get_filename(self):
        return "%s/%s/most_recent.html" % (self.wearer.username, 'tshirts')

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        worn_set = self.wearer.worn_set.all()
        context['sort_by'] = 'recent'
        context['wearings'] = sorted(
                worn_set,
                key=lambda worn: worn.days_worn.first().day,
                reverse=True,
            )
        return context


class WearerFirstWorn(StaticPage):
    template = 'wearers/wearer_type_index.html'

    def get_filename(self):
        return "%s/%s/first_worn.html" % (self.wearer.username, 'tshirts')

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        worn_set = self.wearer.worn_set.all()
        context['sort_by'] = 'first'
        context['wearings'] = sorted(
                worn_set,
                key=lambda worn: worn.days_worn.last().day,
                reverse=True,
            )
        return context


class WearerCSV(StaticPage):
    def get_filename(self):
        return '%s/index.csv' % self.wearer.username

    def create_page(self):
        filename = self.get_filename()
        full_filename = os.path.join(settings.GENERATED_SITES_DIR, filename)
        with open(full_filename, 'w') as handle:
            print(f'>> {full_filename}')
            writer = csv.DictWriter(
                handle,
                fieldnames=['day','wearer','type','slug','name', 'image'],
            )
            writer.writeheader()

            wearings = self.wearer.wearings.select_related(
                    'worn__clothing'
                ).order_by('day')
            for wearing in wearings:
                row = {
                    'day': wearing.day,
                    'wearer': self.wearer,
                    'type': wearing.clothing.type,
                    'slug': wearing.clothing.slug,
                    'name': wearing.clothing.name,
                }
                if wearing.clothing.image:
                    row['image'] = wearing.clothing.image.url
                writer.writerow(row)


class WearerAtom(FeedPage):
    def get_filename(self):
        return '%s/index.atom' % self.wearer.username

    def get_feed_link(self):
        return 'https://%s.hasworn.com/' % self.wearer.username

    def get_feed_url(self):
        return 'https://%s.hasworn.com/index.atom' % self.wearer.username

    def get_feed_title(self):
        return 'What %s has worn' % self.wearer.get_name()

    def get_context(self):
        context = super().get_context()
        context['feed_items'] = self.wearer.wearings.all()[:20]
        return context


class WearerCalendar(CalendarPage):
    def get_filename(self):
        return '%s/index.ics' % self.wearer.username

    def get_feed_name(self):
        return '%s.hasworn.com' % self.wearer.username

    def get_context(self):
        context = super().get_context()
        context['feed_items'] = self.wearer.wearings.all()
        return context


class WearerNotFoundPage(StaticPage):
    template = 'wearers/wearer_404.html'

    def get_filename(self):
        return '%s/404.html' % self.wearer.username

    def get_context(self):
        context = super().get_context()
        context['random_wearings'] = self.wearer.has_worn.order_by('?')
        return context
