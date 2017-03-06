''' Base classes to read json responses into objects '''
import json
import collections
import datetime
import os
import StringIO
import string

from django.conf import settings
from django.core.files.storage import default_storage


class DataOnly(object):pass


# ignore too few public methods witin this file - these models almost always
# don't need a public method because they inherit from the base implementation
# pylint: disable=too-few-public-methods
class Objectifier(object):

    '''
    Class to build class-instance accessors from provided dictionary object
    '''
    object_map = {}

    def _make_data_object(self, value, object_type):
        if object_type != DataOnly and (isinstance(value, dict) or isinstance(value, list)):
            return object_type(dictionary=value)
        else:
            return value

    def __init__(self, dictionary):
        self._build_from_dictionary(dictionary)

    def _build_from_dictionary(self, dictionary):
        ''' Set the attributes of the object from the given dictionary '''
        if isinstance(dictionary, list):
            return
        for item in dictionary:
            if isinstance(dictionary[item], dict):
                self.__setattr__(
                    item,
                    self._make_data_object(
                        dictionary[item], self._object_type_for_name(item, dictionary[item]))
                )
            elif isinstance(dictionary[item], list):
                new_list = [self._make_data_object(item_value, self._object_type_for_name(item, dictionary[item]))
                            for item_value in dictionary[item]]
                self.__setattr__(
                    item,
                    new_list
                )
            else:
                self.__setattr__(item, dictionary[item])

    def _object_type_for_name(self, item_name, item_dictionary):
        '''
        Configure object types in child classes; used when we desire a
        child object for an attribute instead of default Objectifier object
        '''
        object_type = Objectifier
        if item_name in self.object_map:
            object_type = self.object_map[item_name]

        return object_type


class MissingRequiredFieldError(Exception):

    '''
    Exception to be thrown when a required field is missing
    '''

    def __init__(self, value):
        self.value = value
        super(MissingRequiredFieldError, self).__init__()

    def __str__(self):
        return "Missing required field '{}'".format(self.value)


def _build_date_field(json_date_string_value):
    ''' converts json date string to date object '''
    if json_date_string_value is None:
        return None

    try:
        if "T" in json_date_string_value:
            if "." in json_date_string_value:
                format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
            else:
                format_string = "%Y-%m-%dT%H:%M:%SZ"
        else:
            format_string = "%Y-%m-%d"

        return datetime.datetime.strptime(
            json_date_string_value,
            format_string
        )
    except ValueError:
        return None


# Can create one of these, and add some class-specific checks for required
# values, even strip bad values
class JsonObject(Objectifier):

    '''
    Create an python object from a json object
    Can inherit from this class if you like, specifying member overrides
        required_fields - list of field names that must be present to
            instantiate this object
        valid_fields - list of fields that are expected; define this if you
            want to strip unexpected fields from the generate object
    Alternatively, just instantiate one of these from a dictionary object
        instead of json
    '''
    required_fields = []
    valid_fields = None
    date_fields = []

    def __init__(self, json_data=None, dictionary=None):
        if dictionary is None and json_data is not None:
            dictionary = json.loads(json_data)

        for date_field in self.date_fields:
            if date_field in dictionary:
                dictionary[date_field] = _build_date_field(dictionary[date_field])

        if dictionary is not None:
            self._validate_fields(dictionary)
            super(JsonObject, self).__init__(dictionary)
            # self._build_from_dictionary(dictionary)

    def _validate_fields(self, dictionary):
        '''
        Ensures that generated class has required_fields and,
        if specified, that only valid_fields remain
        '''
        for required in self.required_fields:
            if required not in dictionary:
                raise MissingRequiredFieldError(required)
        if self.valid_fields:
            remove_fields = []
            for element in dictionary:
                if element not in self.valid_fields:
                    remove_fields.append(element)
            for remove_field in remove_fields:
                del dictionary[remove_field]

class JsonObjectWithImage(JsonObject):

    def image_url(self, size=48, path='absolute'):
        '''
        Return default avatar unless the user has one

        Specify size=None if you want the original image
        '''
        try:
            if hasattr(self, 'avatar_url') and self.avatar_url is not None:
                usable_sizes = [s[0] for s in self.get_image_sizes() if s[0] >= size] if size else None
                best_image_size = min(usable_sizes) if usable_sizes else None

                # if we are asking for one of the specific sizes but it does not exist, then clean any old ones and regenerate
                if best_image_size and size == best_image_size and not self.have_size(size):
                    self._clean_and_resize_images()

                image_url = self.avatar_url
                if best_image_size and self.have_size(best_image_size):
                    image_url = self._get_specific_size_url(best_image_size)

                if not default_storage.exists(self._strip_proxy_image_url(image_url)):
                    image_url = JsonObjectWithImage.default_image_url()
                elif path == 'absolute' and settings.DEFAULT_FILE_STORAGE != 'django.core.files.storage.FileSystemStorage':
                    image_url = default_storage.url(
                        self._strip_proxy_image_url(image_url)
                    )
            else:
                image_url = JsonObjectWithImage.default_image_url()
        except:
            image_url = JsonObjectWithImage.default_image_url()
        return image_url

    @classmethod
    def default_image_url(cls):
        return "/static/image/empty_avatar.png"

    def _strip_proxy_image_url(self, profileImageUrl):
        if profileImageUrl[:10] == '/accounts/':
            profileImageUrl = profileImageUrl.replace('/accounts/', '')
        return profileImageUrl

    def have_size(self, size):
        test_path = self._strip_proxy_image_url(
            self._get_specific_size_url(size)
        )
        return default_storage.exists(test_path)

    def delete_size(self, size):
        delete_path = self._strip_proxy_image_url(
            self._get_specific_size_url(size)
        )
        default_storage.delete(delete_path)

    def _get_specific_size_url(self, size):
        return "{}-{}.jpg".format(os.path.splitext(self.avatar_url)[0], size)

    def _clean_and_resize_images(self):
        for delete_size in settings.REMOVE_IMAGE_SIZES:
            if self.have_size(delete_size):
                self.delete_size(delete_size)

        image_path = self._strip_proxy_image_url(self.avatar_url)
        if default_storage.exists(image_path):
            from PIL import Image
            original_image = Image.open(
                default_storage.open(image_path)
            )
            self.save_profile_image(original_image, image_path)

    @classmethod
    def get_image_sizes(cls):
        return settings.PROFILE_GENERATE_IMAGE_SIZES

    @classmethod
    def save_profile_image(cls, cropped_example, image_url, new_image_url=None):
        from PIL import Image
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        if not new_image_url:
            new_image_url = image_url

        # Save normal path
        old_image_url_name = os.path.splitext(image_url)[0]
        new_image_url_name = os.path.splitext(new_image_url)[0]
        '''
        There's a slight chance the image won't be deleted since
        an exception might be raised while request for deletion was in progress,
        e.g. because request timed out, in which case the execution will be continued.
        It would be a good thing to delete unused profile images from S3 server by hand.
        '''
        try:
            default_storage.delete(image_url)
        except:
            pass
        cls._save_image(cropped_example, new_image_url)

        # And save special sizes to generate
        for generate_size in cls.get_image_sizes():
            gen_image_url = "{}-{}.jpg".format(new_image_url_name, generate_size[0])
            old_gen_image_url = "{}-{}.jpg".format(old_image_url_name, generate_size[0])
            cropped_image = cls._rescale_image(cropped_example, generate_size[0], generate_size[1])
            try:
                default_storage.delete(old_gen_image_url)
            except:
                pass
            cls._save_image(cropped_image, gen_image_url)

    @classmethod
    def _rescale_image(cls, img, width, height, force=True):
        """Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""
        from PIL import Image as pil
        from cStringIO import StringIO as csio

        max_width = width
        max_height = height
        if not force:
            img.thumbnail((max_width, max_height), pil.ANTIALIAS)
        else:
            from PIL import ImageOps
            img = ImageOps.fit(img, (max_width, max_height,), method=pil.ANTIALIAS)
        tmp = csio()
        img.convert('RGB').save(tmp, 'JPEG')
        output_data = img
        tmp.close()

        return output_data

    @classmethod
    def _save_image(cls, image_data, image_url):
        thumb_io = StringIO.StringIO()
        image_data.convert('RGB').save(thumb_io, format='JPEG')
        if default_storage.exists(image_url):
            default_storage.delete(image_url)

        default_storage.save(image_url, thumb_io)


class JsonParser(object):

    '''
    JsonParser static class to initiate parsing of json into specific
    JsonObject impementations
    '''
    @staticmethod
    def from_json(json_data, object_type=JsonObject, data_filter=None):
        ''' takes json => dictionary / array and processes it accordingly '''
        parsed_json = json.loads(json_data)
        return JsonParser.from_dictionary(parsed_json, object_type, data_filter)

    @staticmethod
    def from_dictionary(dictionary_info, object_type=JsonObject, data_filter=None):
        if isinstance(dictionary_info, list):
            if data_filter:
                for key, value in data_filter.iteritems():
                    dictionary_info = [jo for jo in dictionary_info if jo[key] == value]

            out_objects = []
            for json_dictionary in dictionary_info:
                out_objects.append(object_type(dictionary=json_dictionary))

            return out_objects
        else:
            return object_type(dictionary=dictionary_info)


class CategorisedJsonObject(JsonObject):

    _categorised_parser = None

    def __init__(self, json_data=None, dictionary=None, parser=None):
        self._categorised_parser = parser
        super(CategorisedJsonObject, self).__init__(
            json_data=json_data,
            dictionary=dictionary
        )

    def _object_type_for_name(self, item_name, item_dictionary):
        '''
        Configure object types in child classes; used when we desire a
        child object for an attribute instead of default Objectifier object
        '''
        object_type = CategorisedJsonObject
        if self._categorised_parser and self._categorised_parser._category_property_name in item_dictionary:
            object_type = self._categorised_parser._category_dictionary[
                item_dictionary[self._categorised_parser._category_property_name]]
        elif item_name in self.object_map:
            object_type = self.object_map[item_name]

        return object_type

    def _make_data_object(self, value, object_type):
        if isinstance(value, collections.Iterable):

            if self._categorised_parser and self._categorised_parser._category_property_name in value:
                return self._categorised_parser.from_dictionary(value)

            return object_type(dictionary=value, parser=self._categorised_parser)

        return value


class CategorisedJsonParser(object):

    _category_property_name = "category"
    _category_dictionary = {}

    def __init__(self, category_dictionary, category_property_name="category"):
        self._category_dictionary = category_dictionary
        self._category_property_name = category_property_name

    def from_json(self, json_data):
        ''' takes json => dictionary / array and processes it accordingly '''
        return self.from_dictionary(json.loads(json_data))

    def from_dictionary(self, parsed_json):
        ''' takes dictionary / array and processes it accordingly '''
        if isinstance(parsed_json, list):
            out_objects = []
            for json_dictionary in parsed_json:
                out_objects.append(self.from_dictionary(json_dictionary))

            return out_objects
        else:
            object_type = CategorisedJsonObject
            if self._category_property_name in parsed_json:
                if parsed_json[self._category_property_name] in self._category_dictionary:
                    object_type = self._category_dictionary[
                        parsed_json[self._category_property_name]]

            return object_type(dictionary=parsed_json, parser=self)
