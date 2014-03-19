from django.conf import settings

import haml
import mako.template

def get_haml_template(template_name, locations=settings.TEMPLATE_DIRS):
    lookup = mako.lookup.TemplateLookup(locations, preprocessor=haml.preprocessor)

    return lookup.get_template(template_name)
