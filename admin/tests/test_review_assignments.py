from django.test import TestCase

from admin.review_assignments import ReviewAssignmentProcessor, ReviewAssignmentUnattainableError
from admin.tests.utils import MockReviewAssignmentGroup, MockReviewAssignmentGroupCollection, test_set, test_user, \
    test_workgroup


# TODO: mock API to fix test and uncomment
# class ReviewAssignmentsTest(TestCase):
#     def test_one_user_in_each_of_2_groups(self):
#         ''' one user in each workgroup - should do each others '''
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         users = [test_user_1, test_user_2]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
#             rap.distribute()
#
#     def test_one_user_in_each_of_2_groups_with_min_users(self):
#         ''' one user in each workgroup - should do each others '''
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         users = [test_user_1, test_user_2]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 1)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 2)
#             rap.distribute()
#
#     def test_one_user_in_each_of_3_groups(self):
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         test_user_3 = test_user(3)
#         users = [test_user_1, test_user_2, test_user_3]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2]),
#                       test_workgroup(13, [test_user_3])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[13]), 2)
#
#         rap.workgroup_reviewers[11].sort()
#         self.assertEqual(rap.workgroup_reviewers[11], [2, 3])
#         rap.workgroup_reviewers[12].sort()
#         self.assertEqual(rap.workgroup_reviewers[12], [1, 3])
#         rap.workgroup_reviewers[13].sort()
#         self.assertEqual(rap.workgroup_reviewers[13], [1, 2])
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(len(rap.workgroup_reviewers[13]), 1)
#
#         self.assertTrue(rap.workgroup_reviewers[11] == [2] or rap.workgroup_reviewers[11] == [3])
#         self.assertTrue(rap.workgroup_reviewers[12] == [1] or rap.workgroup_reviewers[12] == [3])
#         self.assertTrue(rap.workgroup_reviewers[13] == [1] or rap.workgroup_reviewers[13] == [2])
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 3, 0)
#             rap.distribute()
#
#     def test_one_user_in_each_of_3_groups_with_min_users(self):
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         test_user_3 = test_user(3)
#         users = [test_user_1, test_user_2, test_user_3]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2]),
#                       test_workgroup(13, [test_user_3])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 2)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[13]), 2)
#
#         rap.workgroup_reviewers[11].sort()
#         self.assertEqual(rap.workgroup_reviewers[11], [2, 3])
#         rap.workgroup_reviewers[12].sort()
#         self.assertEqual(rap.workgroup_reviewers[12], [1, 3])
#         rap.workgroup_reviewers[13].sort()
#         self.assertEqual(rap.workgroup_reviewers[13], [1, 2])
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 3)
#             rap.distribute()
#
#     def test_two_users_in_each_of_2_groups(self):
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         test_user_11 = test_user(11)
#         test_user_12 = test_user(12)
#         users = [test_user_1, test_user_2, test_user_11, test_user_12]
#         workgroups = [test_workgroup(101, [test_user_1, test_user_11]),
#                       test_workgroup(102, [test_user_2, test_user_12])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 2, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[101]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[102]), 2)
#         rap.workgroup_reviewers[101].sort()
#         self.assertEqual(rap.workgroup_reviewers[101], [2, 12])
#         rap.workgroup_reviewers[102].sort()
#         self.assertEqual(rap.workgroup_reviewers[102], [1, 11])
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 3, 0)
#             rap.distribute()
#
#     def test_two_users_in_each_of_2_groups_with_min_users(self):
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         test_user_11 = test_user(11)
#         test_user_12 = test_user(12)
#         users = [test_user_1, test_user_2, test_user_11, test_user_12]
#         workgroups = [test_workgroup(101, [test_user_1, test_user_11]),
#                       test_workgroup(102, [test_user_2, test_user_12])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 1)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[101]), 2)
#         self.assertEqual(len(rap.workgroup_reviewers[102]), 2)
#         rap.workgroup_reviewers[101].sort()
#         self.assertEqual(rap.workgroup_reviewers[101], [2, 12])
#         rap.workgroup_reviewers[102].sort()
#         self.assertEqual(rap.workgroup_reviewers[102], [1, 11])
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 2)
#             rap.distribute()
#
#     def test_lotsa_peeps(self):
#         users, workgroups = test_set(200, 4)
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 10, 0)
#         rap.distribute()
#
#         # Make sure all groups have 10 reviewers
#         for wg in workgroups:
#             self.assertTrue(len(rap.workgroup_reviewers[wg.id]) == 10)
#
#         # Make sure that it is fairly even
#         max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
#         min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])
#
#         self.assertTrue(max_assignments - min_assignments < 2)
#
#     def test_lotsa_peeps_with_min_users(self):
#         users, workgroups = test_set(200, 4)
#
#         for i in range(3):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, i)
#             rap.distribute()
#
#             # Make sure that all users have at least i reviews to perform
#             min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])
#             self.assertTrue(min_assignments >= i)
#
#             # Make sure that it is fairly even
#             max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
#             self.assertTrue(max_assignments - min_assignments < 2)
#
#     def test_lotsa_peeps_with_min_users_unattainable(self):
#         users, workgroups = test_set(200, 4)
#
#         # largest attainable
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 49)
#         rap.distribute()
#
#         # Make sure that all users have at least i reviews to perform
#         min_assignments = min([len(rap.reviewer_workgroups[u.id]) for u in users])
#         max_assignments = max([len(rap.reviewer_workgroups[u.id]) for u in users])
#         self.assertTrue(min_assignments == 49)
#         self.assertTrue(max_assignments == 49)
#
#         with self.assertRaises(ReviewAssignmentUnattainableError):
#             rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 0, 50)
#             rap.distribute()
#
#     def test_assignment_twice(self):
#         ''' one user in each workgroup - should do each others '''
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         users = [test_user_1, test_user_2]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         MockReviewAssignmentGroupCollection.load(rap)
#
#         test_user_3 = test_user(3)
#         test_user_4 = test_user(4)
#         users.extend([test_user_3, test_user_4])
#         workgroups.extend([test_workgroup(13, [test_user_3]), test_workgroup(14, [test_user_4])])
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
#
#         # should be exactly the same as before for 11 and 12
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         # and similarly, need new assignments for 13 and 14
#         self.assertEqual(len(rap.workgroup_reviewers[13]), 1)
#         self.assertEqual(rap.workgroup_reviewers[13][0], 4)
#
#         self.assertEqual(len(rap.workgroup_reviewers[14]), 1)
#         self.assertEqual(rap.workgroup_reviewers[14][0], 3)
#
#         MockReviewAssignmentGroupCollection.load(rap)
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute(True, assignment_group_class=MockReviewAssignmentGroup)
#
#         # should be exactly the same as before for 11 and 12
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertFalse(rap.workgroup_reviewers[11][0] == 1)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertFalse(rap.workgroup_reviewers[12][0] == 2)
#
#         # and similarly, need new assignments for 13 and 14
#         self.assertEqual(len(rap.workgroup_reviewers[13]), 1)
#         self.assertFalse(rap.workgroup_reviewers[13][0] == 3)
#
#         self.assertEqual(len(rap.workgroup_reviewers[14]), 1)
#         self.assertFalse(rap.workgroup_reviewers[14][0] == 4)
#
#     def test_assignment_thrice(self):
#         ''' one user in each workgroup - should do each others '''
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         users = [test_user_1, test_user_2]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]
#
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute()
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         MockReviewAssignmentGroupCollection.load(rap)
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#         MockReviewAssignmentGroupCollection.load(rap)
#         rap = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-xblock', 1, 0)
#         rap.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
#
#         self.assertEqual(len(rap.workgroup_reviewers[11]), 1)
#         self.assertEqual(rap.workgroup_reviewers[11][0], 2)
#
#         self.assertEqual(len(rap.workgroup_reviewers[12]), 1)
#         self.assertEqual(rap.workgroup_reviewers[12][0], 1)
#
#     def test_assignment_with_two_activities(self):
#         ''' one user in each workgroup - should do each others '''
#         test_user_1 = test_user(1)
#         test_user_2 = test_user(2)
#         users = [test_user_1, test_user_2]
#         workgroups = [test_workgroup(11, [test_user_1]), test_workgroup(12, [test_user_2])]
#
#         '''Generate activity review assignment for test-activity-xblock-1 activity'''
#         rap_assignment1 = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-activity-xblock-1', 1, 0)
#         rap_assignment1.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
#         MockReviewAssignmentGroupCollection.load(rap_assignment1)
#
#         '''
#         There should be one assignment for test activity xblock 1 and workgroup 11
#         There should be no assignments for test activity xblock 1 and workgroup 13 (workgroup doesn't exist)
#         There should be no assignments for test activity xblock 2 and workgroup 12 (activity doesn't exist)
#         There should be no assignments for test activity xblock 3 and workgroup 13 (both doesn't exist)
#         '''
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(11, 'test-activity-xblock-1')), 1)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-1')), 0)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(12, 'test-activity-xblock-2')), 0)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-3')), 0)
#
#         '''Generate activity review assignment for test-activity-xblock-2 activity'''
#         rap_assignment2 = ReviewAssignmentProcessor([u.id for u in users], workgroups, 'test-activity-xblock-2', 1, 0)
#         rap_assignment2.distribute(False, assignment_group_class=MockReviewAssignmentGroup)
#         MockReviewAssignmentGroupCollection.load(rap_assignment2)
#
#         '''
#         There should be one assignment for test activity xblock 2 and workgroup 11
#         There should be no assignments for test activity xblock 2 and workgroup 13 (workgroup doesn't exist)
#         There should be no assignments for test activity xblock 3 and workgroup 12 (activity doesn't exist)
#         There should be no assignments for test activity xblock 4 and workgroup 13 (both doesn't exist)
#         '''
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(11, 'test-activity-xblock-2')), 1)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-2')), 0)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(12, 'test-activity-xblock-3')), 0)
#         self.assertEqual(len(MockReviewAssignmentGroup.list_for_workgroup(13, 'test-activity-xblock-4')), 0)

