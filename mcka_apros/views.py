import haml
import mako.template
from api_client.api_exec import authenticate
from django.http import HttpResponse

from api_client.api_exec import get_user

def home(request):
    lookup = mako.lookup.TemplateLookup(["templates"],preprocessor=haml.preprocessor)

    # Retrieve a template.
    auth_info = authenticate("staff", "edx")
    template = lookup.get_template('main.html.haml')

    return HttpResponse(template.render_unicode(user = auth_info.user))
