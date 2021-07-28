from os import makedirs, path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string


class StaticPage(object):
    template = None
    object = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_template(self):
        if self.template is None:
            raise ImproperlyConfigured("No template set")
        return self.template

    def get_context(self):
        return {
            "wearer": self.wearer,
            "object": self.object,
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
