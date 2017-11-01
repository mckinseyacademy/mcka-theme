"""
helper methods/utils related to accounts
"""
from urlparse import urljoin

from django.core.urlresolvers import reverse

from .models import UserActivation


class TestUser(object):
    """
    Represents a minimum User object
    """
    id = None
    email = None

    def __init__(self, user_id, email, username='test_user'):
        """
        the plain, old class initializer
        """
        self.id = user_id
        self.email = email
        self.username = username


def get_user_activation_links(user_ids, base_url=''):
    """
    Builds a map of user and activation links

    Args:
        user_ids (list, tuple): user ids
        base_url (string, optional): base url of the server
    Returns:
        dict of the form {user_id: absolute_activation_link}
    Raises:
        TypeError: if user_ids is not list or tuple
    """
    if not isinstance(user_ids, (list, tuple)):
        raise TypeError('Supply a list or tuple of user ids')

    activation_list = UserActivation.objects.filter(user_id__in=user_ids).\
        values_list('user_id', 'activation_key')

    return dict(
        (user_id, create_activation_url(activation_code, base_url))
        for user_id, activation_code in activation_list
    )


def create_activation_url(activation_code, base_url=''):
    """
    Builds activation url from activation code

    if base_url is given then absolute link is returned otherwise relative
    """
    return urljoin(
        base=base_url,
        url=reverse('activate', kwargs={'activation_code': activation_code})
    )


def get_complete_country_name(shorter_name):
    from .forms import COUNTRY_CHOICES  # for breaking cyclic import

    """
    Transforms shorter country names to complete one
    e.g; `mn` to `Mongolia`

    returns short_name if complete not found in mapping
    """
    return dict(COUNTRY_CHOICES).get(
        shorter_name.upper(), shorter_name
    )
