from django.conf import settings
from django.contrib.auth import views, logout
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView


class WearerContext:
    def get_context_data(self):
        context = super().get_context_data()
        context['wearer'] = self.request.user
        context['COMMIT_SHA'] = settings.COMMIT_SHA
        return context


class Home(WearerContext, TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['panel.html']
        else:
            return ['login.html']


class All(WearerContext, TemplateView):
    template_name='all.html'

    def get_context_data(self):
        context = super().get_context_data()
        worn_set = self.request.user.worn_set.all()
        context['wearings'] = sorted(
                worn_set,
                key=lambda worn: worn.days_worn.first().day,
                reverse=True,
            )
        return context


class Login(views.LoginView):
    template_name='login.html'

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse('admin:index')
        else:
            return reverse('homepage')


class Logout(views.LogoutView):
    template_name='logout.html'

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse('homepage'))

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Standard View class dispatcher.
        # (Don't logout on GET, only POST)
        if request.method.lower() in self.http_method_names:
            handler = getattr(
                self,
                request.method.lower(),
                self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)
