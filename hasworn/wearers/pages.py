from datetime import date
from hasworn.pages import ModelPage, StaticPage


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
