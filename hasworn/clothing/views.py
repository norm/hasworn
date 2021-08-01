from django.views.generic import CreateView

from .models import Wearing


class CreateWearing(CreateView):
    model = Wearing
    fields = ('day', 'worn')

    def get_success_url(self):
        self.request.user.generate_wearer_site_wearing(self.object)
        return '/'
