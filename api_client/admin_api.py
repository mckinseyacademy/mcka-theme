''' API calls with respect to users and authentication '''
from .json_object import JsonParser as JP
#from . import user_models
from .json_requests import GET, POST, DELETE
import json

from . import admin_models

from django.conf import settings

ADMIN_API = 'api/admin'

def create_program(program_hash):
    ''' register the given program within the openedx server '''
    program_keys = ["name", "private_name", "start_date", "end_date",]
    data = {program_key: program_hash[program_key] for program_key in program_keys}

    response = POST(
        '{}/{}/programs/'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            ADMIN_API,
        ),
        data
    )
    
    return JP.from_json(response.read(), admin_models.Program)

def get_program_list():
    ''' pull a list of all programs into system'''
    response = GET(
        '{}/{}/programs'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            ADMIN_API,
        )
    )

    return JP.from_json(response.read(), admin_models.Program)

def get_program_detail(program_id):

    response = GET(
        '{}/{}/programs/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            ADMIN_API,
            program_id,
        )
    )

    return JP.from_json(response.read(), admin_models.Program)

def delete_program(program_id):

    response = DELETE(
        '{}/{}/programs/{}'.format(
            settings.API_MOCK_SERVER_ADDRESS,
            ADMIN_API,
            program_id,
        )
    )

    return (response.code == 204)
