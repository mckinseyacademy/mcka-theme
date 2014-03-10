import haml
import mako.template
from django.http import HttpResponse

from api_client.api_exec import get_user

def home(request):
    lookup = mako.lookup.TemplateLookup(["templates"],preprocessor=haml.preprocessor)

    # Retrieve a template.
    template = lookup.get_template('main.html.haml')

    return HttpResponse(template.render_unicode(user = get_user(9)))
