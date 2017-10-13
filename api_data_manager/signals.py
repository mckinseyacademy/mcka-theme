from django.dispatch import Signal, receiver

from .user_data import UserDataManager
from .group_data import GroupDataManager

user_data_updated = Signal(providing_args=['user_ids', 'data_type'])
group_data_updated = Signal(providing_args=['group_ids', 'data_type'])


@receiver(user_data_updated)
def user_data_updated_handler(sender, *args, **kwargs):
    user_ids = kwargs.get('user_ids')
    user_property = kwargs.get('data_type')

    for user_id in user_ids:
        data_manager = UserDataManager(user_id=user_id)
        data_manager.delete_cached_data(user_property)


@receiver(group_data_updated)
def group_data_updated_handler(sender, *args, **kwargs):
    group_ids = kwargs.get('group_ids')
    user_property = kwargs.get('data_type')

    for group_id in group_ids:
        data_manager = GroupDataManager(group_id=group_id)
        data_manager.delete_cached_data(user_property)
