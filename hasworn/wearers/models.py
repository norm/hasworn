from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Wearer(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length = 30,
        unique = True,
        help_text = _(
            'Required. 30 characters or less. '
            'Letters, digits, and hyphens only.'
        ),
        validators=[
            validators.RegexValidator(
                r'^[a-z][a-z0-9-]+$',
                _(
                    'Enter a valid username. '
                     'The username must start with a letter, '
                     'and may contain only letters, numbers and hyphens.'
                ),
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    # names are more complex than first/last so don't even try
    first_name = None
    last_name = None
    name = models.CharField(
        _('name'), 
        max_length = 1024,
        blank = True,
        null = True,
    )

    USERNAME_FIELD = 'username'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.username

    def get_name(self):
        if not self.name:
            return self.username
        else:
            return self.name

    @property
    def wearings(self):
        from hasworn.clothing.models import Wearing
        return Wearing.objects.filter(worn__wearer=self)

    def generate_wearer_site(self):
        from .pages import WearerPage
        WearerPage(wearer=self).create()
