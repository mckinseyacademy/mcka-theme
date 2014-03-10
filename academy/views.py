import haml
import mako.template
from django.http import HttpResponse

def home(request):
    lookup = mako.lookup.TemplateLookup(["various", "templates", "paths"],preprocessor=haml.preprocessor)

    # Retrieve a template.
    template = lookup.get_template('main.html.haml')

    return HttpResponse(template.render_unicode())
