import urllib2 as url_access
import datetime
import copy
import os

from django.conf import settings
from django.utils.translation import ugettext as _

from api_client import user_api
from api_client.json_object import JsonParser as JP
from api_client.api_error import ApiError

class ActivationError(Exception):
    '''
    Exception to be thrown when an activation failure occurs
    '''
    def __init__(self, value):
        self.value = value
        super(ActivationError, self).__init__()

    def __str__(self):
        return "ActivationError '{}'".format(self.value)


def user_activation_with_data(user_id, user_data, activation_record):
    try:
        # Make sure they'll be inactive while updating fields, then we explicitly activate them
        user_data["is_active"] = False
        updated_user = user_api.update_user_information(user_id, user_data)
    except ApiError as e:
        raise ActivationError(e.message)

    # if we are still okay, then activate in a separate operation
    try:
        user_api.activate_user(user_id)
    except ApiError as e:
        raise ActivationError(e.message)

    activation_record.delete()


def is_future_start(date):
    current_time = datetime.datetime.now()
    if date <= current_time:
        return False
    else:
        return True

def save_new_client_image(old_image_url, new_image_url, client):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage

    new_image_url_name = os.path.splitext(new_image_url)[0]
    old_image_url_name = os.path.splitext(old_image_url)[0]

    if default_storage.exists(old_image_url):

        io_new_client_image(old_image_url, new_image_url)

        for generate_size in settings.GENERATE_IMAGE_SIZES:
            old_gen_image_url = "{}-{}.jpg".format(old_image_url_name, generate_size)
            new_gen_image_url = "{}-{}.jpg".format(new_image_url_name, generate_size)
            io_new_client_image(old_gen_image_url, new_gen_image_url)
        client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + "{}.jpg".format(new_image_url_name)})

def io_new_client_image(old_gen_image_url, new_gen_image_url):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage

    thumb_io = StringIO.StringIO()
    original = Image.open(default_storage.open(old_gen_image_url))
    original.convert('RGB').save(thumb_io, format='JPEG')
    cropped_image_path = default_storage.save(new_gen_image_url, thumb_io)
    default_storage.delete(old_gen_image_url)
