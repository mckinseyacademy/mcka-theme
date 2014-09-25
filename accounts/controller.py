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

    old_image_url_40 = old_image_url[:-4] + '-40.jpg'
    old_image_url_120 = old_image_url[:-4] + '-120.jpg'
    new_image_url_40 = new_image_url[:-4] + '-40.jpg'
    new_image_url_120 = new_image_url[:-4] + '-120.jpg'

    if default_storage.exists(old_image_url):

        thumb_io_120 = StringIO.StringIO()
        thumb_io_40 = StringIO.StringIO()
        thumb_io = StringIO.StringIO()

        original = Image.open(default_storage.open(old_image_url))
        original.convert('RGB').save(thumb_io, format='JPEG')
        cropped_image_path = default_storage.save(new_image_url, thumb_io)

        original_40 = Image.open(default_storage.open(old_image_url_40))
        original_40.convert('RGB').save(thumb_io_40, format='JPEG')
        cropped_image_path_40 = default_storage.save(new_image_url_40, thumb_io_40)

        original_120 = Image.open(default_storage.open(old_image_url_120))
        original_120.convert('RGB').save(thumb_io_120, format='JPEG')
        cropped_image_path_120 = default_storage.save(new_image_url_120, thumb_io_120)

        default_storage.delete(old_image_url)
        default_storage.delete(old_image_url_40)
        default_storage.delete(old_image_url_120)
        client.update_and_fetch(client.id,  {'logo_url': '/accounts/' + new_image_url})

def save_profile_image(cropped_example, image_url):

    import StringIO
    from PIL import Image
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile

    cropped_image_120 = _rescale_image(cropped_example, 120, 120)
    cropped_image_40 = _rescale_image(cropped_example, 40, 40)

    thumb_io_120 = StringIO.StringIO()
    thumb_io_40 = StringIO.StringIO()
    thumb_io = StringIO.StringIO()

    cropped_image_120.convert('RGB').save(thumb_io_120, format='JPEG')
    cropped_image_40.convert('RGB').save(thumb_io_40, format='JPEG')
    cropped_example.convert('RGB').save(thumb_io, format='JPEG')

    if default_storage.exists(image_url):
        default_storage.delete(image_url)
    if default_storage.exists(image_url[:-4] + '-40.jpg'):
        default_storage.delete(image_url[:-4] + '-40.jpg')
    if default_storage.exists(image_url[:-4] + '-120.jpg'):
        default_storage.delete(image_url[:-4] + '-120.jpg')

    cropped_image_120_path = default_storage.save(image_url[:-4] + '-120.jpg', thumb_io_120)
    cropped_image_40_path = default_storage.save(image_url[:-4] + '-40.jpg', thumb_io_40)
    cropped_image_path = default_storage.save(image_url[:-4] + '.jpg', thumb_io)


def _rescale_image(img, width, height, force=True):
    """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
    from PIL import Image as pil
    from cStringIO import StringIO

    max_width = width
    max_height = height
    if not force:
        img.thumbnail((max_width, max_height), pil.ANTIALIAS)
    else:
        from PIL import ImageOps
        img = ImageOps.fit(img, (max_width, max_height,), method=pil.ANTIALIAS)
    tmp = StringIO()
    img.convert('RGB').save(tmp, 'JPEG')
    output_data = img
    tmp.close()

    return output_data
