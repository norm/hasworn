from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView

from .models import Wearing


class CreateWearing(CreateView):
    model = Wearing
    fields = ('day', 'worn')

    def get_success_url(self):
        self.request.user.generate_wearer_site_wearing(self.object)
        return '/'


class DeleteWearing(DeleteView):
    model = Wearing

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        year = self.object.day.year
        worn_pk = self.object.worn.pk
        self.object.delete()
        self.request.user.generate_wearer_site_deleted(worn_pk, year)
        return HttpResponseRedirect('/')
