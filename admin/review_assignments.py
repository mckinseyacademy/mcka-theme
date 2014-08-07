import random
import datetime

from .models import ReviewAssignmentGroup

class ReviewAssignmentUnattainableError(Exception):
    pass


class ReviewAssignmentProcessor(object):

    def __init__(self, user_ids, workgroups, review_target, user_target):

        self.user_ids = user_ids
        self.workgroups = workgroups
        self.review_target = review_target
        self.user_target = user_target

        # Maintain double-lookup maps for assignments
        self.workgroup_reviewers = {wg.id: [] for wg in self.workgroups}
        self.reviewer_workgroups = {us: [] for us in self.user_ids}

    def assert_possible(self):
        for wg in self.workgroups:
            possible_reviewers = [u for u in self.user_ids if not u in wg.users]
            if len(possible_reviewers) < self.review_target:
                raise ReviewAssignmentUnattainableError()

        for user_id in self.user_ids:
            possible_workgroups = [wg for wg in self.workgroups if not user_id in wg.users]
            if len(possible_workgroups) < self.user_target:
                raise ReviewAssignmentUnattainableError()


    def distribute_pass(self, workgroups_in_need, user_ids):
        random.shuffle(user_ids)
        users_dispensed = []

        for workgroup in workgroups_in_need:
            possible_ids = [i for i in user_ids if not i in self.workgroup_reviewers[workgroup.id] and not i in workgroup.users and not i in users_dispensed]
            if len(possible_ids) > 0:
                self.workgroup_reviewers[workgroup.id].append(possible_ids[0])
                self.reviewer_workgroups[possible_ids[0]].append(workgroup.id)
                users_dispensed.append(possible_ids[0])
                break


    def distribute(self):
        self.assert_possible()

        workgroups_in_need = self.workgroups
        users_available = self.user_ids

        review_threshold = 1
        user_threshold = 1

        # Maintain double-lookup maps for assignments
        self.workgroup_reviewers = {wg.id: [] for wg in self.workgroups}
        self.reviewer_workgroups = {us: [] for us in self.user_ids}

        # cycle until we've met the minimum reviews per workgroup
        while review_threshold <= self.review_target or len(workgroups_in_need) > 0:

            self.distribute_pass(workgroups_in_need, users_available)
            workgroups_in_need = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < min(review_threshold, self.review_target)]
            users_available = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < user_threshold]

            # only 1 avilable might have only its users available
            if len(workgroups_in_need) < 1 and review_threshold <= self.review_target:
                review_threshold += 1

            if len(users_available) < 1 or (len(workgroups_in_need) == 1 and len([u for u in users_available if not u in workgroups_in_need[0].users]) == 0):
                user_threshold += 1

            workgroups_in_need = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < min(review_threshold, self.review_target)]
            users_available = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < user_threshold]

        # Now also cycle until we've met the minimum reviews per user
        users_in_need = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < self.user_target]
        user_review_threshold = 1
        workgroups_available = []
        while len(users_in_need) > 0:
            # pass out the workgroups that have fewer reviewers first
            while len(workgroups_available) < 1:
                user_review_threshold += 1
                workgroups_available = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < user_review_threshold]

            self.distribute_pass(workgroups_available, users_in_need)

            workgroups_available = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < user_review_threshold]
            users_in_need = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < self.user_target]



    def store_assignments(self, course_id, xblock_id):
        for wg in self.workgroups:
            now = datetime.datetime.today()
            rag = ReviewAssignmentGroup.create(
                "Assignment group for {}".format(wg.id),
                {
                    "assignment_date": now.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    "xblock_id": xblock_id,
                }
            )
            rag.add_course(course_id)
            rag.add_workgroup(wg.id)
            for user_id in self.workgroup_reviewers[wg.id]:
                rag.add_user(user_id)
