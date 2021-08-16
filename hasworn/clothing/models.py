from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import itertools

from hasworn.wearers.models import Wearer


def image_location(instance, filename):
    return '%s/%s.%s.jpg' % (
            instance.type,
            instance.slug,
            instance.updated_at.strftime('%Y%m%d%H%M%S'),
        )


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
    image = models.ImageField(
        upload_to = image_location,
        blank = True,
        null = True,
    )

    def __str__(self):
        return u'%s (%s)' % (self.name, self.type)

    @property
    def static_site_url(self):
        return '/%s/%s' % (self.type_plural, self.slug)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        else:
            return 'http://img.hasworn.com/%s.jpg' % self.slug

    @property
    def type_plural(self):
        return '%ss' % self.type

    def save(self, *args, **kwargs):
        if not self.id and not self.slug:
            slug = slugify(self.name)[:127]
            for count in itertools.count(10):
                if not Clothing.objects.filter(slug=slug).exists():
                    break
                diff = "-%d" % count
                slug = "%s%s" % (slug[:127-len(diff)], diff)
            self.slug = slug
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

    @property
    def last_worn(self):
        return self.days_worn.first()

    @property
    def times_worn(self):
        times = self.days_worn.count()
        if times == 0:
            return 'never'
        elif times == 1:
            return 'once'
        elif times == 2:
            return 'twice'
        else:
            return '%s times' % times

    @property
    def last_worn_days_ago(self):
        delta = relativedelta(date.today(), self.last_worn.day)
        if delta.years:
            if delta.years == 1:
                return '1 year ago'
            else:
                return '%s years ago' % delta.years
        else:
            if delta.months >= 3:
                return '%s months ago' % delta.months
            else:
                if self.last_worn_days == 0:
                    return 'today'
                elif self.last_worn_days == 1:
                    return 'yesterday'
        return '%s days ago' % self.last_worn_days

    @property
    def last_worn_days(self):
        return (date.today() - self.last_worn.day).days

    @property
    def average_days_between_wearings(self):
        if self.days_worn.count() < 2:
            # use the days since the first anything worn, -1
            return (
                    (date.today() - self.wearer.wearings.last().day).days
                    + 1
                )
        else:
            sum = int(self.days_worn.aggregate(
                        models.Sum('days_since_last')
                    )['days_since_last__sum'])
            total_days = sum + self.last_worn_days
            return int(total_days / self.days_worn.count())

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
    days_since_last = models.IntegerField(
        blank = True,
        null = True,
    )

    @property
    def clothing(self):
        return self.worn.clothing

    def update_days_since_last(self):
        try:
            previous = Wearing.objects.filter(
                    worn = self.worn,
                    day__lt = self.day,
                ).order_by('-day')[0]
            self.days_since_last = (self.day - previous.day).days
        except IndexError:
            pass

        # wearings can be added retrospectively, so make sure "future"
        # wearings now have the right value too
        try:
            next = Wearing.objects.filter(
                    worn = self.worn,
                    day__gt = self.day,
                ).order_by('day')[0]
            next.days_since_last = (next.day - self.day).days
            next.save()
        except IndexError:
            pass

    def save(self, *args, **kwargs):
        if not self.days_since_last:
            self.update_days_since_last()
        super().save(*args, **kwargs)

    def __str__(self):
        return u'%s worn by %s on %s' % (
            self.worn.clothing,
            self.worn.wearer,
            self.day,
        )
