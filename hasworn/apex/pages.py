from hasworn.pages import StaticPage


class ApexPage(StaticPage):
    template = 'apex.html'

    def get_filename(self):
        return 'index.html'
