import codecs

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

ERROR_PAGES = ['403', '404', '500', '503']


class Command(BaseCommand):
    help = 'Generates the static html error pages from the templates'

    def handle(self, *args, **options):
        for error_page in ERROR_PAGES:
            html_content = render_to_string('{}.haml'.format(error_page), {})
            with codecs.open(
                    './static/pages/{}.html'.format(error_page),
                    'w',
                    encoding="utf-8"
            ) as static_error_page_file:
                static_error_page_file.write(html_content)
