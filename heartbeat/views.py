from django.db import connection
from django.db.utils import DatabaseError
from api_client.api_error import ApiError
from api_client.json_requests import GET
from django.conf import settings
from django.http import HttpResponse
import json

def heartbeat(request):

    API = 'api/server/'
    output = {}

    try:
        try:
            response = GET(
            '{}/{}'.format(
                settings.API_SERVER_ADDRESS, API
                )
            )
            output['API'] = True
        except ApiError as fail:
            output['API'] = unicode(fail.message)
    except:
        output['API'] = False

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT CURRENT_DATE")
        cursor.fetchone()
        output['SQL'] = True
    except DatabaseError as fail:
        output['SQL'] = unicode(fail) 

    return HttpResponse(json.dumps(output), content_type="application/json")