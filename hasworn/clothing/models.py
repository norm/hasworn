from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.humanize.templatetags.humanize import apnumber
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import itertools

from hasworn.utils import ordinal
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

    def user_worn(self, user):
        return Worn.objects.get(clothing=self, wearer=user)

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
    no_longer = models.CharField(
        max_length = 255,
        blank = True,
        null = True,
    )

    @property
    def last_worn(self):
        return self.days_worn.first()

    @property
    def first_worn(self):
        return self.days_worn.last()

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
    def absolute_static_site_url(self):
        return 'https://%s.hasworn.com/%s/%s' % (
                self.wearer, self.clothing.type_plural, self.clothing.slug
            )

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
    def position_in_most_worn_by_days_between(self):
        avg = self.wearer.most_worn_by_days_between()
        for count, worn in enumerate(avg):
            if worn.pk == self.pk:
                return count+1
        return 0

    @property
    def average_days_between_wearings(self):
        count = self.days_worn.count()
        if count < 5:
            # use the days since the first anything worn, -1
            return (
                    (date.today() - self.wearer.wearings.last().day).days
                    + 1
                )
        else:
            # scenario 1: a tshirt that is worn only on Christmas Day should
            # have an average of every 365 days -- it should not drastically
            # reduce because today is Jan 1st
            # 
            # scenario 2: a tshirt previously worn frequently but no longer
            # should have its average grow over time -- to reflect that it
            # is no longer a regularly worn tshirt
            # 
            # therefore only increase the average wear with the current days
            # since last wearing once it is *larger* than the average
            days_worn = self.days_worn.filter(days_since_last__gt = 0)
            average = int(
                days_worn.aggregate(
                    models.Avg('days_since_last')
                )['days_since_last__avg']
            )
            if self.last_worn_days < average:
                return average
            else:
                total = int(
                    days_worn.aggregate(
                        models.Sum('days_since_last')
                    )['days_since_last__sum']
                )
                total += self.last_worn_days
                return int(total / count)

    @property
    def wear_today_score(self):
        if self.no_longer:
            # no longer worn means v low score
            return -10

        if self.days_worn.count() == 0:
            # never worn has a (probably winning) high score
            return 10

        score = 0
        if self.last_worn_days < self.average_days_between_wearings:
            # when worn more recently than the average,
            # not yet time to wear it again
            score -= 1
        else:
            # when not worn for a while, give 1 point per year over the average
            score += (
                (self.last_worn_days - self.average_days_between_wearings)
                / 365
            )
        return score

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

    @property
    def tweet_text(self):
        return '%s #daily #tshirt %s — %s' % (
                self.clothing.name,
                self.worn.absolute_static_site_url,
                self.summary_text,
            )

    @property
    def summary_text(self):
        total_worn = self.worn.days_worn.count()
        if total_worn == 1:
            return self.first_wearing_text
        elif total_worn < 5:
            return self.low_wearing_count_text
        else:
            last = self.worn.days_worn.all()[1]
            if (self.day - last.day).days > 365:
                return self.long_gap_wearing_text
            else:
                return self.wearing_text

    @property
    def first_wearing_text(self):
        return 'This is the first time I\'ve worn this tshirt.'

    @property
    def low_wearing_count_text(self):
        previous_wearing = self.worn.days_worn.all()[1]
        delta = relativedelta(self.day, previous_wearing.day)
        if delta.years > 0:
            if delta.months > 9:
                gap = 'nearly %s years ago' % apnumber(delta.years + 1)
            elif delta.years == 1:
                if delta.months < 2:
                    gap = 'a year ago'
                else:
                    gap = 'over a year ago'
            else:
                if delta.months < 2:
                    gap = '%d years ago' % delta.years
                else:
                    gap = 'over %d years ago' % delta.years
        elif delta.months > 2:
            gap = 'over %d months ago' % delta.months
        elif delta.months == 0 and delta.days == 1:
            gap = 'yesterday'
        else:
            days = self.day - previous_wearing.day
            gap = '%d days ago' % days.days
        return (
            'This is the %s time I\'ve worn this tshirt,'
            ' the last time was %s.' % (
                ordinal(self.worn.days_worn.count()),
                gap,
            )
        )

    @property
    def long_gap_wearing_text(self):
        previous_wearing = self.worn.days_worn.all()[1]
        delta = relativedelta(self.day, previous_wearing.day)
        if delta.months > 9:
            gap = 'nearly %s years' % ordinal(delta.years + 1)
        elif delta.years == 1:
            gap = 'over a year'
        else:
            gap = 'over %d years' % delta.years
        return (
            'This is the %s time I\'ve worn this since %s,'
            ' and the first time in %s.' % (
                ordinal(self.worn.days_worn.count()),
                self.worn.first_worn.day.strftime('%B %Y'),
                gap,
            )
        )

    @property
    def wearing_text(self):
        year_ago = date.today() - timedelta(days=365)
        return (
            'This is the %s time I\'ve worn this since %s,'
            ' and the %s time in the past twelve months.'
            ' It is my %s most frequently worn tshirt. '
            ' I wear it on average every %.f days.' % (
                ordinal(self.worn.days_worn.count()),
                self.worn.first_worn.day.strftime('%B %Y'),
                ordinal(self.worn.days_worn.filter(day__gte=year_ago).count()),
                ordinal(self.worn.position_in_most_worn_by_days_between),
                self.worn.average_days_between_wearings,
            )
        )

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
