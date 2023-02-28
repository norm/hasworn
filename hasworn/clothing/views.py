from datetime import date
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

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
        worn = Worn.objects.create(
            clothing = self.object,
            wearer = self.request.user,
        )
        if 'wearing' in self.get_form_kwargs()['data']:
            wearing = Wearing.objects.create(
                worn = worn,
                day = date.today(),
            )
            self.request.user.added_wearing(wearing)
        return super().form_valid(form)

    def get_success_url(self):
        return '/'


class UpdateClothing(UpdateView):
    model = Clothing
    fields = ('name', 'description', 'image')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worn = context['object'].user_worn(self.request.user)
        worn_url = reverse('update-worn', kwargs={'pk': worn.pk})
        context.update({
            'worn_url': worn_url,
            'no_longer': worn.no_longer,
        })
        return context

    def get_success_url(self):
        return '/'


class UpdateWorn(UpdateView):
    model = Worn
    fields = ('no_longer',)

    def get_success_url(self):
        return '/all/'
