import logging

from django.core.cache import cache

_logger = logging.getLogger(__name__)


class DataManager(object):
    cache_key_prefix = ''
    cache_unique_identifier = ''
    cache_expire_time = (60 * 1) * 10  # 10 minutes

    def get_cache_key(self, property_name, identifier=None):
        return '{cache_key_prefix}_{cache_property_name}_{cache_unique_identifier}'.format(
            cache_key_prefix=self.cache_key_prefix,
            cache_property_name=property_name,
            cache_unique_identifier=identifier or self.cache_unique_identifier,
        )

    def delete_cached_data(self, property_name):
        cache_key = self.get_cache_key(property_name=property_name)
        cache.delete(cache_key)

    def get_cached_data(self, property_name):
        return cache.get(self.get_cache_key(property_name))

    def set_cached_data(self, property_name, data, expiry_time=None):
        cache_key = self.get_cache_key(property_name)

        _logger.info(
            'Setting Cache for {}\'s `{}` with data `{}` on key `{}`'.format(
                self.cache_key_prefix, property_name, data, cache_key
            )
        )

        return cache.set(cache_key, data, expiry_time or self.cache_expire_time)

    @staticmethod
    def flush_cache():
        cache.clear()
