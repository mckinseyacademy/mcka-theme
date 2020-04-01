"""
helper methods/utils related to accounts
"""
import random
import string
from urllib.parse import urljoin
import logging

from django.urls import reverse
from .models import UserActivation
from api_client.api_error import ApiError
from api_client.group_api import add_users_to_group, PERMISSION_GROUPS, remove_user_from_group
from lib.authorization import permission_groups_map
from api_client.user_api import get_filtered_users

log = logging.getLogger(__name__)


class TestUser(object):
    """
    Represents a minimum User object
    """
    id = None
    email = None

    def __init__(self, user_id, email, username='test_user', is_staff=False):
        """
        the plain, old class initializer
        """
        self.id = user_id
        self.email = email
        self.username = username
        self.is_staff = is_staff


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


def make_user_manager(user_id):
    """
    Adds user to MANAGER permission group.
    """
    try:
        add_users_to_group(
            [user_id],
            permission_groups_map()[PERMISSION_GROUPS.MANAGER]
        )
    except ApiError as e:
        if e.code == 409:
            log.warning(
                """
                Attempt to make user with id: {} a manager.
                User already is a manager.
                """.format(user_id)
            )
        else:
            raise


def unmake_user_manager(user_id):
    """
    Removes user from MANAGER permission group.
    """
    try:
        remove_user_from_group(
            user_id,
            permission_groups_map()[PERMISSION_GROUPS.MANAGER]
        )
    except ApiError as e:
        if e.code == 404 or e.code == 410:
            log.warning(
                """
                Attempt to remove manager permission from user with id: {}.
                User is not a manager.
                """.format(user_id)
            )
        else:
            raise


def get_user_by_email(email):
    query_params = {
        'email': str(email),
    }
    users = get_filtered_users(query_params)['results']
    return users[0] if users else None


def get_organization_by_user_email(user_email):
    organization_user = get_user_by_email(user_email)
    organization_id = organization_user['organizations'][0]['id']
    return organization_id


def get_random_string(size=32, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))
