''' API calls with respect to organizations '''
import json
from django.utils.translation import ugettext as _
from django.conf import settings
from urllib import urlencode

from lib.util import DottableDict
from .api_error import api_error_protect, ERROR_CODE_MESSAGES

from .json_object import JsonParser as JP
from .json_object import JsonObject, JsonObjectWithImage
from .json_requests import GET, POST, DELETE, PATCH

ORGANIZATION_API = getattr(settings, 'ORGANIZATION_API', 'api/server/organizations')

@api_error_protect
def create_organization(organization_name, organization_data=None, organization_object=JsonObjectWithImage):
    ''' create a new organization '''
    data = {
        "name": organization_name,
    }

    data.update(organization_data)

    response = POST(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
        ),
        data
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def fetch_organization(organization_id, organization_object=JsonObjectWithImage):
    ''' fetch organization by id '''
    response = GET(
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return JP.from_json(response.read(), organization_object)


@api_error_protect
def fetch_organization_user_ids(organization_id):
    """ fetch organization user ids """
    response = GET(
        '{}/{}/{}/users?view=ids'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return json.loads(response.read())


@api_error_protect
def fetch_organization_group_ids(organization_id):
    """ fetch organization group ids """
    response = GET(
        '{}/{}/{}/groups?view=ids'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return json.loads(response.read())


@api_error_protect
def get_users_by_enrolled(organization_id, user_object=JsonObjectWithImage, *args, **kwargs):
    ''' fetch organization users list, with additional courses enrolled flag '''
    qs_params = {}
    qs_params.update(kwargs)

    response = GET(
        '{}/{}/{}/users/?{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
            urlencode(qs_params)
        )
    )

    return JP.from_json(response.read(), user_object)

@api_error_protect
def fetch_organization_from_url(url, organization_object=JsonObjectWithImage):
    ''' fetch organization by id '''
    response = GET(url)
    return JP.from_json(response.read(), organization_object)

@api_error_protect
def get_organizations(organization_object=JsonObjectWithImage):
    ''' fetch all organizations '''
    response = GET(
        '{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
        )
    )

    return JP.from_json(response.read(), organization_object)

@api_error_protect
def get_organization_groups(organization_id, groups_object=JsonObject, *args, **kwargs):
    ''' fetch all organization groups '''
    qs_params = {}
    qs_params.update(kwargs)

    response = GET(
        '{}/{}/{}/groups?{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
            urlencode(qs_params)
        )
    )

    return JP.from_json(response.read(), groups_object)

@api_error_protect
def delete_organization(organization_id):
    ''' delete organization by id '''
    response = DELETE(
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        )
    )

    return (response.code == 204)

@api_error_protect
def update_organization(organization_id, organization_data, organization_object=JsonObjectWithImage):
    ''' update existing organization '''
    response = PATCH(
        '{}/{}/{}/'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
        ),
        organization_data
    )

    return JP.from_json(response.read(), organization_object)

@api_error_protect
def add_user_to_organization(organization_id, user_id):
    ''' Add the specified user to the given organization '''
    data = {
        "id": user_id,
    }

    response = POST(
        '{}/{}/{}/users/'.format(settings.API_SERVER_ADDRESS, ORGANIZATION_API, organization_id),
        data,
    )

    return (response.code == 201)

@api_error_protect
def get_grade_complete_count(organization_id, organization_object=JsonObject, *args, **kwargs):
    qs_params = {}
    for karg in kwargs:
        if isinstance(kwargs[karg], list):
            qs_params[karg] = ",".join(kwargs[karg])
        else:
            qs_params[karg] = kwargs[karg]
    response = GET(
        '{}/{}/{}/metrics/?{}'.format(
            settings.API_SERVER_ADDRESS,
            ORGANIZATION_API,
            organization_id,
            urlencode(qs_params),
        )
    )

    return JP.from_json(response.read(), organization_object)


ORGANIZATION_ERROR_CODE_MESSAGES = {
    "create_organization": {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
    "update_organization": {
        403: _("Permission Denied"),
        401: _("Invalid data"),
    },
}
ERROR_CODE_MESSAGES.update(ORGANIZATION_ERROR_CODE_MESSAGES)
