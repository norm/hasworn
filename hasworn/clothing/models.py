from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from hasworn.wearers.models import Wearer


class Clothing(models.Model):
    """
    An item of clothing, of a specific type.
    """
    class Type(models.TextChoices):
        TSHIRT = 'tshirt', _('tshirt')

    class Meta:
        verbose_name = 'Clothing'
        verbose_name_plural = 'Clothing'

    name = models.CharField(
        max_length = 256,
    )
    description = models.CharField(
        max_length = 2048,
        blank = True,
        null = True,
    )
    slug = models.SlugField(
        max_length = 128,
        unique = True,
    )
    type = models.CharField(
        max_length = 32,
        choices = Type.choices,
        default = Type.TSHIRT,
    )
    created_by = models.ForeignKey(
        Wearer,
        models.SET_NULL,
        blank = True,
        null = True,
    )
    created_at = models.DateTimeField(
        auto_now_add = True,
    )
    updated_at = models.DateTimeField(
        auto_now = True,
    )
    worn_by = models.ManyToManyField(
        Wearer,
        through = 'Worn',
        related_name = 'has_worn',
    )

    def __str__(self):
        return u'%s (%s)' % (self.name, self.type)

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            self.slug = slugify(self.name)[:127]
        super().save(*args, **kwargs)


class Worn(models.Model):
    """ An item of clothing that has been worn by a wearer. """
    class Meta:
        unique_together = ('wearer', 'clothing')

    wearer = models.ForeignKey(
        Wearer,
        on_delete = models.CASCADE,
    )
    clothing = models.ForeignKey(
        Clothing,
        on_delete = models.CASCADE,
    )

    def __str__(self):
        return u'%s (worn by %s)' % (
            self.clothing,
            self.wearer,
        )


class Wearing(models.Model):
    """
    A Wearer wearing an item of Clothing on a given day.
    """
    class Meta:
        ordering = ['-day']
        unique_together = ('worn', 'day')

    worn = models.ForeignKey(
        Worn,
        on_delete = models.CASCADE,
        related_name = 'days_worn',
    )
    day = models.DateField(
        default = timezone.now,
    )

    @property
    def clothing(self):
        return self.worn.clothing

    def __str__(self):
        return u'%s worn by %s on %s' % (
            self.worn.clothing,
            self.worn.wearer,
            self.day,
        )
