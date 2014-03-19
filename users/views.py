import haml
import mako.template
from django.http import HttpResponse
from api_client import api_exec

import haml_mako.templates as haml

# Create your views here.

#@login_required
def user_profile(request):
    template = haml.get_haml_template('users/user_profile.html.haml')
    return HttpResponse(template.render_unicode(user=api_exec.get_user(request.user.id)))
