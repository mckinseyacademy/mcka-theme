''' API calls with respect to users and authentication '''
from .json_object import JsonParser as JP
#from . import user_models
from .json_requests import GET, POST, DELETE
import json

from django.conf import settings

ADMIN_API = 'api/admin'

def create_client(client_hash):
    # TODO - this is a stub
    ''' register the given client within the openedx server '''
    client_keys = ["company", "contact_name", "phone", "email",]
    data = {client_key: client_hash[client_key] for client_key in client_keys}

    # response = POST(
    #     '{}/{}/organization'.format(settings.API_SERVER_ADDRESS, ADMIN_API),
    #     data
    # )
    
    data["id"] = "FAKE_COMPANY_ID"
    return JP.from_json(json.dumps(data))

def get_client_list():
    # TODO - this is a stub
    ''' pull a list of all clients into system'''
    clients = [
        {
            "name": "Rolling Stones",
            "id": "STONES",
        },
        {
            "name": "The Beatles",
            "id": "BEATLES",
        },
        {
            "name": "Floating Boats",
            "id": "BOATS",
        },
        {
            "name": "Lux Deluxe",
            "id": "LUX",
        },
    ]

    return JP.from_json(json.dumps(clients))

def get_client_detail(client_id):
    # TODO - this is a stub
    client_detail = {
        "id": "STONES",
        "name": "Rolling Stones",
        "members": "Mick, Keith, Daryl / Bill, Ron, Charlie"
    }

    return JP.from_json(json.dumps(client_detail))

def create_program(program_hash):
    # TODO - this is a stub
    ''' register the given client within the openedx server '''
    program_keys = ["company", "contact_name", "phone", "email",]
    data = {program_key: program_hash[program_key] for program_key in program_keys}
    data["id"] = "FAKE_PROGRAM_ID"

    # response = POST(
    #     '{}/{}/program'.format(settings.API_SERVER_ADDRESS, ADMIN_API),
    #     data
    # )
    
    return JP.from_json(json.dumps(data))

def get_program_list():
    # TODO - this is a stub
    ''' pull a list of all programs into system'''
    programs = [
        {
            "name": "Game of Thrones",
            "id": "THRONES",
        },
        {
            "name": "Marvel's Agents of S.H.I.E.L.D.",
            "id": "SHIELD",
        },
        {
            "name": "The Big Bang Theory",
            "id": "BIGBANG",
        },
        {
            "name": "How I Met Your Mother",
            "id": "MOTHER",
        },
    ]

    return JP.from_json(json.dumps(programs))

def get_program_detail(program_id):
    # TODO - this is a stub
    program_detail = {
        "id": "THRONES",
        "name": "Game of Thrones",
        "members": "Mick, Keith, Daryl / Bill, Ron, Charlie"
    }

    return JP.from_json(json.dumps(program_detail))
