import random
import datetime

from django.utils.translation import ugettext as _

from .models import ReviewAssignmentGroup


class ReviewAssignmentUnattainableError(Exception):
    pass


class ReviewAssignmentProcessor(object):

    def __init__(self, user_ids, workgroups, xblock_id, review_target, user_target):

        self.user_ids = user_ids
        self.workgroups = workgroups
        self.review_target = review_target
        self.user_target = user_target
        self.xblock_id = xblock_id

    def _init_review_groups(self, delete_existing, *args, **kwargs):

        # Maintain double-lookup maps for assignments
        self.workgroup_reviewers = {wg.id: [] for wg in self.workgroups}
        self.reviewer_workgroups = {us: [] for us in self.user_ids}

        assignment_group_class = kwargs.get('assignment_group_class', ReviewAssignmentGroup)

        for wg in self.workgroups:
            assignment_groups = assignment_group_class.list_for_workgroup(wg.id, self.xblock_id)
            for rag in assignment_groups:
                if delete_existing:
                    assignment_group_class.delete(rag.id)
                else:
                    for user in rag.get_users():
                        self.reviewer_workgroups[user.id].append(wg.id)
                        self.workgroup_reviewers[wg.id].append(user.id)

    def assert_possible(self):
        for wg in self.workgroups:
            possible_reviewers = [u for u in self.user_ids if not u in wg.user_ids]
            if len(possible_reviewers) < self.review_target:
                raise ReviewAssignmentUnattainableError()

        for user_id in self.user_ids:
            possible_workgroups = [wg for wg in self.workgroups if not user_id in wg.user_ids]
            if len(possible_workgroups) < self.user_target:
                raise ReviewAssignmentUnattainableError()


    def distribute_pass(self, workgroups_in_need, user_ids):
        random.shuffle(user_ids)
        users_dispensed = []

        for workgroup in workgroups_in_need:
            possible_ids = [i for i in user_ids if not i in self.workgroup_reviewers[workgroup.id] and not i in workgroup.user_ids and not i in users_dispensed]
            if len(possible_ids) > 0:
                self.workgroup_reviewers[workgroup.id].append(possible_ids[0])
                self.reviewer_workgroups[possible_ids[0]].append(workgroup.id)
                users_dispensed.append(possible_ids[0])
                break


    def distribute(self, delete_existing=False, *args, **kwargs):
        self.assert_possible()

        review_threshold = 1
        user_threshold = 1

        self._init_review_groups(delete_existing, *args, **kwargs)

        workgroups_in_need = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < min(review_threshold, self.review_target)]
        users_available = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < user_threshold]

        # cycle until we've met the minimum reviews per workgroup
        while review_threshold <= self.review_target or len(workgroups_in_need) > 0:

            self.distribute_pass(workgroups_in_need, users_available)
            workgroups_in_need = [wg for wg in self.workgroups if len(self.workgroup_reviewers[wg.id]) < min(review_threshold, self.review_target)]
            users_available = [us for us in self.user_ids if len(self.reviewer_workgroups[us]) < user_threshold]

            # only 1 avilable might have only its users available
            if len(workgroups_in_need) < 1 and review_threshold <= self.review_target:
                review_threshold += 1

            if len(users_available) < 1 or (len(workgroups_in_need) == 1 and len([u for u in users_available if not u in workgroups_in_need[0].user_ids]) == 0):
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


    def store_assignments(self, course_id):
        for wg in self.workgroups:
            # check for existing assignments
            existing_assignments = ReviewAssignmentGroup.list_for_workgroup(wg.id, self.xblock_id)
            if len(existing_assignments) > 0:
                # pick one existing assignment
                rag = existing_assignments[0]

                # delete other (superfluous) assignments
                for ea in existing_assignments[1:]:
                    ReviewAssignmentGroup.delete(ea.id)

                old_reviewers = set([u.id for u in rag.get_users()])
                new_reviewers = set(self.workgroup_reviewers[wg.id])

                for user_id in new_reviewers - old_reviewers:
                    rag.add_user(user_id)

                for user_id in old_reviewers - new_reviewers:
                    rag.remove_user(user_id)

            else:
                now = datetime.datetime.today()
                rag = ReviewAssignmentGroup.create(
                    _("Assignment group for {wg_id}").format(wg_id=wg.id),
                    {
                        "assignment_date": now.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "xblock_id": self.xblock_id,
                    }
                )
                rag.add_course(course_id)
                rag.add_workgroup(wg.id)
                for user_id in self.workgroup_reviewers[wg.id]:
                    rag.add_user(user_id)
