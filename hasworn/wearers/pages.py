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
