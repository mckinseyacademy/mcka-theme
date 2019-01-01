import math
import os
from mock import mock

from lib.utils import DottableDict
from mcka_apros.settings import DELETION_FLAG_NAMESPACE, DELETION_FLAG_SWITCH_NAME

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Create your tests here.

# disable no-member 'cos the members are getting created from the json
# and some others that we don't care about for tests
# pylint: disable=no-member,line-too-long,too-few-public-methods,missing-docstring,too-many-public-methods,
# pointless-statement,unused-argument,protected-access,maybe-no-member,invalid-name

def test_user(id):
    return DottableDict({"id": id, "name": "test_user_{}".format(id)})


def test_workgroup(id, users):
    user_ids = []
    for user in users:
        user_ids.append(user.id)
    return DottableDict({"id": id, "users": users, "user_ids": user_ids})


def test_set(num_users, workgroup_size):
    users = [test_user(i) for i in range(num_users)]
    workgroups = [test_workgroup(j, [u for u in users if int(math.floor(u.id / workgroup_size)) == j]) for j in
                  range(int(math.ceil(num_users / workgroup_size)))]
    return users, workgroups


class MockUser(object):
    id = None

    def __init__(self, user_id):
        self.id = user_id


class MockReviewAssignmentGroup(object):
    id = "fake_id"

    def __init__(self, workgroup, xblock_id):
        self.workgroups = []
        self.users = []
        self.xblock_id = xblock_id

        self.add_workgroup(workgroup.id)
        MockReviewAssignmentGroupCollection.workgroup_lookup[workgroup.id] = [self]

    def add_workgroup(self, workgroup):
        self.workgroups.append(workgroup)

    def add_user(self, user_id):
        self.users.append(MockUser(user_id))

    def get_users(self):
        return self.users

    @classmethod
    def list_for_workgroup(cls, workgroup_id, xblock_id=None):
        review_assignment_groups = MockReviewAssignmentGroupCollection.workgroup_lookup.get(workgroup_id, [])
        if xblock_id:
            review_assignment_groups = [rag for rag in review_assignment_groups if rag.xblock_id == xblock_id]
        return review_assignment_groups

    @classmethod
    def delete(cls, group_id):
        # will only get called when deleting everything, so for mock okay to just reset complete list
        MockReviewAssignmentGroupCollection.workgroup_lookup = {}


class MockReviewAssignmentGroupCollection(object):
    workgroup_lookup = {}

    @classmethod
    def load(cls, review_assignment_processor):
        cls.workgroup_lookup = {}
        for wg in review_assignment_processor.workgroups:
            rag = MockReviewAssignmentGroup(wg, review_assignment_processor.xblock_id)
            for user_id in review_assignment_processor.workgroup_reviewers[wg.id]:
                rag.add_user(user_id)


def get_deletion_waffle_switch():
    return '{}.{}'.format(DELETION_FLAG_NAMESPACE, DELETION_FLAG_SWITCH_NAME)


def make_side_effect_raise_value_error():
    thrown_error = mock.Mock()
    thrown_error.reason = "I have no idea, but luckily it is irrelevant for the test"

    def _raise(*args, **kwargs):
        raise ValueError(thrown_error)

    return _raise
