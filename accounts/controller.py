import urllib2 as url_access
import datetime
import copy

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

    old_image_url_48 = old_image_url[:-4] + '-48.jpg'
    old_image_url_160 = old_image_url[:-4] + '-160.jpg'
    new_image_url_48 = new_image_url[:-4] + '-48.jpg'
    new_image_url_160 = new_image_url[:-4] + '-160.jpg'

    if default_storage.exists(old_image_url):

        thumb_io_160 = StringIO.StringIO()
        thumb_io_48 = StringIO.StringIO()
        thumb_io = StringIO.StringIO()

        original = Image.open(default_storage.open(old_image_url))
        original.convert('RGB').save(thumb_io, format='JPEG')
        cropped_image_path = default_storage.save(new_image_url, thumb_io)

        original_48 = Image.open(default_storage.open(old_image_url_48))
        original_48.convert('RGB').save(thumb_io_48, format='JPEG')
        cropped_image_path_48 = default_storage.save(new_image_url_48, thumb_io_48)

        original_160 = Image.open(default_storage.open(old_image_url_160))
        original_160.convert('RGB').save(thumb_io_160, format='JPEG')
        cropped_image_path_160 = default_storage.save(new_image_url_160, thumb_io_160)

        default_storage.delete(old_image_url)
        default_storage.delete(old_image_url_48)
        default_storage.delete(old_image_url_160)
        client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + new_image_url})

