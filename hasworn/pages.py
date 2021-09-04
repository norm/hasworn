from os import makedirs, path
from datetime import datetime, time
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils import feedgenerator
import icalendar


class StaticPage:
    wearer = None
    template = None
    object = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.object = self.get_object()

    def get_object(self):
        return None

    def get_template(self):
        if self.template is None:
            raise ImproperlyConfigured("No template set")
        return self.template

    def get_context(self):
        return {
            "wearer": self.wearer,
            "object": self.object,
            "COMMIT_SHA": settings.COMMIT_SHA or 'development',
        }

    def render_page(self):
        template_name = self.get_template()
        context = self.get_context()
        return render_to_string(template_name, context)

    def get_filename(self):
        return "norm/index.html"

    def write_file(self, filename, content):
        full_filename = path.join(settings.GENERATED_SITES_DIR, filename)
        directory = path.dirname(full_filename)
        if not path.exists(directory):
            makedirs(directory)
        with open(full_filename, 'w') as handle:
            handle.write(content)

    def create_page(self):
        content = self.render_page()
        filename = self.get_filename()
        self.write_file(filename, content)

    def create(self):
        self.create_page()


class ModelPage(StaticPage):
    model = None

    def get_object(self):
        queryset = self.get_queryset()
        pk = getattr(self, 'pk', None)
        if pk:
            queryset = queryset.filter(pk=pk)
        else:
            slug = getattr(self, 'slug', None)
            if slug:
                queryset = queryset.filter(slug=slug)
            else:
                raise NoWayJose
        try:
            obj = queryset.get()
        except:
            raise NopeNothing
        return obj

    def get_model(self):
        return self.model

    def get_queryset(self):
        model = self.get_model()
        if model:
            return model._default_manager.all()
        else:
            raise NuhUh


class FeedPage(StaticPage):
    feed_title = None
    feed_link = None
    feed_url = None
    feed_description = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feed = feedgenerator.Atom1Feed(
            title = self.get_feed_title(),
            link = self.get_feed_link(),
            feed_url = self.get_feed_url(),
            description = None,
        )

    def get_feed_title(self):
        if self.feed_title is not None:
            return self.feed_title
        raise NoFeedTitle

    def get_feed_link(self):
        if self.feed_link is not None:
            return self.feed_link
        raise NoFeedLink

    def get_feed_url(self):
        if self.feed_url is not None:
            return self.feed_url
        raise NoFeedUrl

    def get_feed_description(self):
        if self.feed_description is not None:
            return self.feed_description
        if 'feed_description' in kwargs:
            return kwargs['feed_description']
        raise NoFeedDescription

    def render_page(self):
        context = self.get_context()
        for item in context['feed_items']:
            description = '<p>%s wore %s on %s.' % (
                    self.wearer.get_name(),
                    item.clothing,
                    item.day,
                )
            if item.clothing.image:
                description += '<img src="%s" alt="">' % item.clothing.image.url
            description += '</p>'
            self.feed.add_item(
                    title = item.clothing.name,
                    author_link = 'https://%s.hasworn.com' % self.wearer.username,
                    author_name = self.wearer.get_name(),
                    link = 'https://%s.hasworn.com%s' % (
                            self.wearer.username,
                            item.clothing.static_site_url
                        ),
                    pubdate = item.day,
                    updateddate = item.day,
                    description = description,
                )

    def write_file(self, filename):
        full_filename = path.join(settings.GENERATED_SITES_DIR, filename)
        directory = path.dirname(full_filename)
        if not path.exists(directory):
            makedirs(directory)
        with open(full_filename, 'w') as handle:
            print('->', full_filename)
            self.feed.write(handle, 'utf-8')

    def create_page(self):
        self.render_page()
        filename = self.get_filename()
        self.write_file(filename)


class CalendarPage(StaticPage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        title = self.get_feed_name()
        self.calendar = icalendar.Calendar()
        self.calendar.add('version', '2.0')
        self.calendar.add(
            'prodid',
            '-//com.hasworn//%s//' % title,
        )
        self.calendar.add('summary', title)
        self.calendar.add('X-WR-CALNAME', title)
        self.calendar.add('X-WR-CALDESC', title)

    def render_page(self):
        context = self.get_context()
        for item in context['feed_items']:
            event = icalendar.Event()
            event.add('uid', '%s-%s' % (item.day, item.clothing.slug))
            event.add('summary', item.clothing.name)
            event.add('dtstart', item.day)
            event.add('dtstamp', datetime.combine(item.day, time()))
            self.calendar.add_component(event)
        return self.calendar.to_ical().decode('utf-8')
