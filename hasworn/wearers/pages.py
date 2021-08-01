import csv
from datetime import date
from django.conf import settings
from hasworn.pages import ModelPage, StaticPage
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
        return context


class WearerTypeIndex(StaticPage):
    template = 'wearers/wearer_type_index.html'

    def get_filename(self):
        return "%s/%s/index.html" % (self.wearer.username, 'tshirts')

    def get_context(self, **kwargs):
        context = super().get_context(**kwargs)
        context['wearings'] = self.wearer.most_worn()
        return context


class WearerCSV(StaticPage):
    def get_filename(self):
        return '%s/index.csv' % self.wearer.username

    def create_page(self):
        filename = self.get_filename()
        full_filename = os.path.join(settings.GENERATED_SITES_DIR, filename)
        with open(full_filename, 'w') as handle:
            print('->', full_filename)
            writer = csv.DictWriter(
                handle,
                fieldnames=['day','type','slug','name'],
            )
            writer.writeheader()

            wearings = self.wearer.wearings.select_related(
                    'worn__clothing'
                ).order_by('day')
            for wearing in wearings:
                writer.writerow({
                    'day': wearing.day,
                    'type': wearing.clothing.type,
                    'slug': wearing.clothing.slug,
                    'name': wearing.clothing.name,
                })
