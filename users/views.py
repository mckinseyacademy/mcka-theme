import haml
import mako.template
from django.http import HttpResponse
from api_client import api_exec

# Create your views here.
#@login_required


def user_profile(request):
    template = get_haml_template('users/user_profile.html.haml')
    return HttpResponse(template.render_unicode(user=api_exec.get_user(request.user.id)))

# TODO: Move this to it's own helper


def get_haml_template(template_name, locations=["templates"]):
    lookup = mako.lookup.TemplateLookup(locations, preprocessor=haml.preprocessor)

    template = lookup.get_template(template_name)

    return template
