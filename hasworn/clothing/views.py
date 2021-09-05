from datetime import date
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DeleteView

from .models import Clothing, Wearing, Worn


class CreateWearing(CreateView):
    model = Wearing
    fields = ('day', 'worn')

    def get_success_url(self):
        self.request.user.added_wearing(self.object)
        return '/'


class DeleteWearing(DeleteView):
    model = Wearing

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        year = self.object.day.year
        worn_pk = self.object.worn.pk
        self.object.delete()
        self.request.user.deleted_wearing(worn_pk, year)
        return HttpResponseRedirect('/')


class CreateClothing(CreateView):
    model = Clothing
    fields = ('name', 'description', 'image')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        self.object.created_by = self.request.user
        self.object.save()
        if 'wearing' in self.get_form_kwargs()['data']:
            worn = Worn.objects.create(
                clothing = self.object,
                wearer = self.request.user,
            )
            wearing = Wearing.objects.create(
                worn = worn,
                day = date.today(),
            )
            self.request.user.added_wearing(wearing)
        return super().form_valid(form)

    def get_success_url(self):
        return '/'
