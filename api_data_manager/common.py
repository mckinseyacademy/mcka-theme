import logging

from django.core.cache import cache
from django.conf import settings

_logger = logging.getLogger(__name__)


class DataManager(object):
    cache_key_prefix = ''
    cache_unique_identifier = ''
    cache_expire_time = settings.DEFAULT_CACHE_TIMEOUT

    def get_cache_key(self, property_name, identifier=None):
        return '{cache_key_prefix}_{cache_property_name}_{cache_unique_identifier}'.format(
            cache_key_prefix=self.cache_key_prefix,
            cache_property_name=property_name,
            cache_unique_identifier=identifier or self.cache_unique_identifier,
        )

    def delete_cached_data(self, property_name):
        cache_key = self.get_cache_key(property_name=property_name)
        cache.delete(cache_key)

    def get_cached_data(self, property_name, parsers=[], alt_property_name=None):
        data = cache.get(self.get_cache_key(alt_property_name)) if alt_property_name else None
        data = data or cache.get(self.get_cache_key(property_name))

        # if parsers are passed, then pass data through them,
        # otherwise return raw data
        if parsers and data is not None:
            for parser in parsers:
                method = parser.get('method')
                params = parser.get('params')

                try:
                    data = method(data, params) if params else method(data)
                except Exception as e:
                    _logger.error('Failed parsing data for property `{}` with exception `{}`'
                                  ' Skipping parsing'.format(property_name, e))
                    break
        return data

    def set_cached_data(self, property_name, data, expiry_time=None):
        cache_key = self.get_cache_key(property_name)

        _logger.info(
            'Setting Cache for {}\'s `{}` on key `{}`'.format(
                self.cache_key_prefix, property_name, cache_key
            )
        )

        return cache.set(cache_key, data, expiry_time or self.cache_expire_time)

    @staticmethod
    def flush_cache():
        cache.clear()
