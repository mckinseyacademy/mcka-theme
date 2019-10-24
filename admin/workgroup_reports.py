import copy
import datetime
from collections import OrderedDict

from django.conf import settings
from django.utils.translation import ugettext as _

from api_client import course_api, user_api, group_api
from api_client.organization_models import Organization
from api_client.project_models import Project
from lib.utils import DottableDict
from .controller import load_course, GROUP_WORK_REPORT_DEPTH
from .models import WorkGroup, WorkGroupV2StageXBlock, GROUP_PROJECT_V2_GRADING_STAGES
from .models import WorkGroupActivityXBlock


def _shallow_merge_dicts(dict1, dict2):
    result = {}
    result.update(dict1)
    result.update(dict2)
    return result


class GroupProjectV1Stages(object):
    UPLOAD = 'upload'
    EVALUATION = 'evaluation'
    GRADE = 'grade'
    GRADED = 'graded'


INDIVIDUAL_STAGES = [GroupProjectV1Stages.EVALUATION, GroupProjectV1Stages.GRADE]
COMPLETION_STAGES = [GroupProjectV1Stages.UPLOAD, GroupProjectV1Stages.EVALUATION, GroupProjectV1Stages.GRADE]

IRRELEVANT = _('--')
NOT_APPLICABLE = _('n/a')

GP_V1_STAGES = OrderedDict([
    (GroupProjectV1Stages.UPLOAD, DottableDict({'name': _("Upload"), 'deadline': IRRELEVANT})),
    (GroupProjectV1Stages.EVALUATION, DottableDict({'name': _("Evaluation"), 'deadline': IRRELEVANT})),
    (GroupProjectV1Stages.GRADE, DottableDict({'name': _("Review"), 'deadline': IRRELEVANT})),
    (GroupProjectV1Stages.GRADED, DottableDict({'name': _("Grading"), 'deadline': IRRELEVANT})),
])

BLANK_ACTIVITY = DottableDict({
    "name": _("This activity does not exist"),
    "grade_type": None,
    "stages": GP_V1_STAGES,
    "stage_count": 4
})

BLANK_ACTIVITY_STATUS = DottableDict({
    "ta_graded": False,
    "review_groups": [],
    "stages": OrderedDict(
        (stage_id, _shallow_merge_dicts(stage_data, {'deadline': NOT_APPLICABLE, 'status': IRRELEVANT}))
        for stage_id, stage_data in GP_V1_STAGES.items()
    ),
    "stage_count": 4
})

BLANK_V2_STAGE_ID = 'blank_stage'
BLANK_V2_STAGE_STATUS = DottableDict({
    'status': IRRELEVANT,
    'is_grading_stage': False,
})

V2_NO_STAGES_AVAILABLE = _('No Stages')


class StageCompletionStatus(object):
    IRRELEVANT = 'irrelevant'
    COMPLETE = 'complete'
    INCOMPLETE = 'incomplete'
    INCOMPLETE_OVERDUE = 'incomplete overdue'


class WorkgroupCompletionData(object):
    projects = None
    completions = None
    course = None
    workgroup_id = None

    project_workgroups = {}
    project_activities = {}
    user_review_assignments = {}

    activity_xblocks = {}
    stage_blocks = {}

    def _get_activity_xblock(self, act_id):
        if act_id not in self.activity_xblocks:
            self.activity_xblocks[act_id] = WorkGroupActivityXBlock.fetch_from_activity(self.course.id, act_id)
        return self.activity_xblocks[act_id]

    def _get_stage_xblock(self, uri):
        if uri not in self.stage_blocks:
            self.stage_blocks[uri] = WorkGroupV2StageXBlock.fetch_from_uri(uri)
        return self.stage_blocks[uri]

    def __init__(self, course_id, group_id=None, restrict_to_users_ids=None, request=None):
        self.activity_xblocks = {}
        self.course = load_course(course_id, depth=GROUP_WORK_REPORT_DEPTH, request=request)
        self.restrict_to_users_ids = restrict_to_users_ids
        self.group_project_lookup = {gp.id: gp for gp in self.course.group_projects}

        if group_id is None:
            self.projects = [
                p for p in Project.fetch_projects_for_course(course_id) if p.content_id in self.group_project_lookup
            ]
        else:
            self.workgroup_id = int(group_id)
            self.projects = [Project.fetch(WorkGroup.fetch(self.workgroup_id).project)]

        self.completions = self._load_completions_data(course_id)
        self._load()

    @staticmethod
    def _make_completion_key(content_id, user_id, stage=None):
        format_string = '{}_{}' if stage is None else '{}_{}_{}'
        return format_string.format(content_id, user_id, stage)

    def _load_project_workgroup_status(self, project, pw):
        for u in pw.users:
            for a in self.project_activities[project.id]:
                group_xblock = self._get_activity_xblock(a.id)
                assignment_groups = user_api.get_user_groups(u.id, group_type='reviewassignment',
                                                             data__xblock_id=group_xblock.id)
                review_assignments = [wg for ag in assignment_groups for wg in group_api.get_workgroups_in_group(ag.id)]
                if u.id not in self.user_review_assignments:
                    self.user_review_assignments[u.id] = {}
                self.user_review_assignments[u.id][group_xblock.id] = [
                    self.project_workgroups[project.id][ra.id]
                    for ra in review_assignments if
                    ra.id in self.project_workgroups[project.id]
                ]

    def _load_completions_data(self, course_id):
        completions = {}

        course_users = course_api.get_course_details_users(course_id).get('results', [])
        for user in course_users:
            username = user['username']
            user_id = user['id']
            user_completions = course_api.get_block_completions(
                course_id=course_id,
                username=username,
            )
            for completion in user_completions:
                if completion.is_complete():
                    completion_key = WorkgroupCompletionData._make_completion_key(
                        content_id=completion.id,
                        user_id=user_id,
                    )
                    completions[completion_key] = completion

        return completions

    def _load(self):
        for project in self.projects:
            if project.organization:
                organization = Organization.fetch(project.organization)
                project.organization_name = organization.display_name
            self.project_workgroups[project.id] = {
                w_id: WorkGroup.fetch_with_members(w_id)
                for w_id in project.workgroups
            }
            group_project = next((
                gp
                for gp in self.course.group_projects
                if gp.id == project.content_id
            ))
            project.name = group_project.name
            self.project_activities[project.id] = group_project.activities

            # load up user review assignments
            if self.workgroup_id:
                self._load_project_workgroup_status(
                    project,
                    self.project_workgroups[project.id][self.workgroup_id],
                )
            else:
                for k, pw in self.project_workgroups[project.id].items():
                    self._load_project_workgroup_status(project, pw)

    def build_report_data(self):
        total_group_count = 0
        projects = []
        for project in self.projects:
            group_project = self.group_project_lookup[project.content_id]
            if group_project.is_v2:
                project_data = self.get_v2_data(project)
            else:
                project_data = self.get_v1_data(project)
            total_group_count += project_data.group_count
            projects.append(project_data)

        return {
            "projects": projects,
            "course": self.course,
            "total_group_count": total_group_count,
        }

    def format_date_value(self, date_value):
        if date_value is None:
            return IRRELEVANT
        return date_value.strftime(settings.SHORT_DATE_FORMAT)

    def get_v1_data(self, p):
        def is_complete(group_xblock, user_ids, stage):
            if stage is not None and stage == GroupProjectV1Stages.GRADE and group_xblock.ta_graded:
                return None

            if stage is not None and stage == GroupProjectV1Stages.GRADED:
                stage = None

            return all(
                WorkgroupCompletionData._make_completion_key(
                    group_xblock.id,
                    u_id,
                    stage,
                ) in self.completions
                for u_id in user_ids
            )

        def review_link(course_id, workgroup, activity=None):
            if activity:
                return "/courses/{}/group_work/{}?seqid={}".format(course_id, workgroup.id, activity.id)
            return "/courses/{}/group_work/{}".format(course_id, workgroup.id)

        def get_due_date(group_xblock, date_name):
            if date_name == GroupProjectV1Stages.GRADED:  # graded and grade share the same milestone
                date_name = GroupProjectV1Stages.GRADE
            if hasattr(group_xblock, "milestone_dates"):
                return getattr(group_xblock.milestone_dates, date_name, None)
            return None

        def formatted_milestone_date(group_xblock, date_name):
            date_value = get_due_date(group_xblock, date_name)
            return self.format_date_value(date_value)

        def report_completion_boolean(stage_completed, due_date=None):
            if stage_completed is None:
                return StageCompletionStatus.IRRELEVANT
            if stage_completed:
                return StageCompletionStatus.COMPLETE
            elif due_date and due_date > datetime.datetime.now():
                return StageCompletionStatus.INCOMPLETE
            return StageCompletionStatus.INCOMPLETE_OVERDUE

        def get_stage_data(stage_id, is_complete, due_date, review_link=None):
            result = {
                'status': report_completion_boolean(is_complete, due_date),
                'is_grading_stage': stage_id == GroupProjectV1Stages.GRADE,
            }
            if review_link is not None:
                result['link'] = review_link
            return DottableDict(result)

        # only take the first 3 activities
        p.activities = self.project_activities[p.id][0:3]
        p.workgroups = [self.project_workgroups[p.id][self.workgroup_id]] if self.workgroup_id else [
            group for k, group in self.project_workgroups[p.id].items()
            ]
        p.group_count = len(p.workgroups)

        for activity in p.activities:
            group_xblock = self._get_activity_xblock(activity.id)
            activity.stages = copy.deepcopy(GP_V1_STAGES)

            for stage_key in list(activity.stages.keys()):
                activity.stages[stage_key]['deadline'] = formatted_milestone_date(group_xblock, stage_key)

            activity.stage_count = len(activity.stages)
            activity.grade_type = _("TA Graded") if group_xblock.ta_graded else _("Peer Graded")

        remove_groups = set()
        for group in p.workgroups:
            if self.restrict_to_users_ids is not None:
                group.users = [user for user in group.users if user.id in self.restrict_to_users_ids]

            if not group.users:
                remove_groups.add(group.id)
                continue

            group.review_link = review_link(self.course.id, group)
            group.activity_statuses = []
            for activity in p.activities:
                group_xblock = self._get_activity_xblock(activity.id)
                activity_status = DottableDict({'ta_graded': group_xblock.ta_graded})
                activity_status.stages = OrderedDict(
                    (stage_id, get_stage_data(
                        stage_id,
                        is_complete(group_xblock, [user.id for user in group.users], stage_id),
                        get_due_date(group_xblock, stage_id),
                        review_link(self.course.id, group, activity) if stage_id == GroupProjectV1Stages.GRADE else None
                    ))
                    for stage_id in activity.stages
                )

                group.activity_statuses.append(activity_status)

            while len(group.activity_statuses) < 3:
                group.activity_statuses.append(BLANK_ACTIVITY_STATUS)

            for user in group.users:
                user.activity_statuses = []
                user.max_review_count = 0
                if self.workgroup_id:
                    organizations = user_api.get_user_organizations(user.id)
                    user.company = organizations[0].display_name if len(organizations) > 0 else None

                for activity in p.activities:
                    group_xblock = self._get_activity_xblock(activity.id)
                    user_activity_status = DottableDict()

                    review_groups = self.user_review_assignments[user.id][group_xblock.id]
                    for review_group in review_groups:
                        review_group.review_link = review_link(self.course.id, review_group, activity)
                        review_group.review_status = report_completion_boolean(
                            is_complete(group_xblock, [u.id for u in review_group.members], None),
                            get_due_date(group_xblock, GroupProjectV1Stages.GRADE))

                    stages = []
                    for stage_id in activity.stages:
                        stage_data = DottableDict()
                        if stage_id in INDIVIDUAL_STAGES:
                            stage_data = get_stage_data(
                                stage_id,
                                is_complete(group_xblock, [user.id], stage_id),
                                get_due_date(group_xblock, stage_id)
                            )
                        elif stage_id == GroupProjectV1Stages.UPLOAD:
                            stage_data = DottableDict({'status': IRRELEVANT, 'is_grading_stage': False})
                        elif stage_id == GroupProjectV1Stages.GRADED:
                            stage_data = get_stage_data(
                                stage_id,
                                is_complete(group_xblock, [u.id for u in group.users], stage_id),
                                get_due_date(group_xblock, stage_id)
                            )

                        if stage_data.get('is_grading_stage', False):
                            stage_data.review_groups = review_groups

                        stages.append((stage_id, stage_data))

                    user_activity_status.stages = OrderedDict(stages)
                    user.activity_statuses.append(user_activity_status)

                while len(user.activity_statuses) < 3:
                    user.activity_statuses.append(BLANK_ACTIVITY_STATUS)

        p.workgroups = [workgroup for workgroup in p.workgroups if workgroup.id not in remove_groups]

        while len(p.activities) < 3:
            # Need copy here, because we assign different indexes below
            p.activities.append(copy.copy(BLANK_ACTIVITY))
        return p

    def _v2_review_link(self, group_id, stage_id=None):
        if stage_id:
            return "/courses/{}/group_work/{}?activate_block_id={}".format(self.course.id, group_id, stage_id)
        return "/courses/{}/group_work/{}".format(self.course.id, group_id)

    def _v2_get_completion_status(self, activity_xblock, stage_xblock, user_ids):
        if activity_xblock.ta_graded and stage_xblock.category in GROUP_PROJECT_V2_GRADING_STAGES:
            return StageCompletionStatus.IRRELEVANT

        complete = all(
            WorkgroupCompletionData._make_completion_key(stage_xblock.id, u_id) in self.completions
            for u_id in user_ids
        )
        if complete:
            return StageCompletionStatus.COMPLETE

        if stage_xblock.close_date and stage_xblock.close_date < datetime.datetime.now():
            return StageCompletionStatus.INCOMPLETE_OVERDUE

        return StageCompletionStatus.INCOMPLETE

    def _v2_is_grading_stage(self, stage_xblock):
        return stage_xblock.category in GROUP_PROJECT_V2_GRADING_STAGES

    def _v2_get_stage_data(self, activity_xblock, stage_xblock, group_id, user_ids):
        is_grading_stage = self._v2_is_grading_stage(stage_xblock)
        result = {
            'status': self._v2_get_completion_status(activity_xblock, stage_xblock, user_ids),
            'is_grading_stage': is_grading_stage,
        }
        if is_grading_stage:
            result['link'] = self._v2_review_link(group_id, stage_xblock.id)
        return DottableDict(result)

    def _v2_get_workgroup_data(self, group, activity_xblocks):
        group_data = DottableDict()
        group_data.id = group.id
        group_data.name = group.name

        users = group.users
        if self.restrict_to_users_ids is not None:
            users = [user for user in group.users if user.id in self.restrict_to_users_ids]

        if not users:
            return None

        group_data.users = users

        group_data.review_link = self._v2_review_link(group.id)
        group_data.activity_statuses = []
        for activity_xblock in activity_xblocks:
            stage_xblocks = self._v2_get_stage_xblocks(activity_xblock)
            activity_status = DottableDict({'ta_graded': activity_xblock.ta_graded})
            activity_status.stages = OrderedDict(
                (
                    stage_xblock.id,
                    self._v2_get_stage_data(activity_xblock, stage_xblock, group.id, [user.id for user in users])
                )
                for stage_xblock in stage_xblocks
            )

            if not activity_status.stages:
                activity_status.stages[BLANK_V2_STAGE_ID] = BLANK_V2_STAGE_STATUS

            group_data.activity_statuses.append(activity_status)

        return group_data

    def _v2_get_workgroup_users_data(self, group, activity_xblocks):
        users = group.users
        if self.restrict_to_users_ids is not None:
            users = [user for user in group.users if user.id in self.restrict_to_users_ids]

        if not users:
            return []

        users_data = []
        for user in users:
            user_data = DottableDict({
                'email': user.email,
                'username': user.username
            })
            if self.workgroup_id:
                organizations = user_api.get_user_organizations(user.id)
                user_data.company = organizations[0].display_name if len(organizations) > 0 else None

            user_data.activity_statuses = []
            for activity_xblock in activity_xblocks:
                user_activity_status = DottableDict()
                user_activity_status.stages = OrderedDict()
                review_groups = self.user_review_assignments[user.id][activity_xblock.id]

                stage_xblocks = self._v2_get_stage_xblocks(activity_xblock)
                for stage_xblock in stage_xblocks:
                    stage_data = self._v2_get_stage_data(activity_xblock, stage_xblock, group.id, [user.id])
                    if self._v2_is_grading_stage(stage_xblock):
                        stage_data.review_groups = copy.deepcopy(review_groups)
                        for review_group in stage_data.review_groups:
                            review_group.review_link = self._v2_review_link(review_group.id, stage_xblock.id)
                            review_group.review_status = self._v2_get_completion_status(
                                activity_xblock, stage_xblock, [u.id for u in review_group.members]
                            )

                    user_activity_status.stages[stage_xblock.id] = stage_data

                if not user_activity_status.stages:
                    user_activity_status.stages[BLANK_V2_STAGE_ID] = BLANK_V2_STAGE_STATUS

                user_data.activity_statuses.append(user_activity_status)

            users_data.append(user_data)

        return users_data

    def _v2_get_stage_xblocks(self, activity_xblock):
        return [self._get_stage_xblock(stage.uri) for stage in activity_xblock.children]

    def get_v2_data(self, p):
        # only take the first 3 activities
        if self.workgroup_id:
            target_workgroups = [self.project_workgroups[p.id][self.workgroup_id]]
        else:
            target_workgroups = list(self.project_workgroups[p.id].values())

        activities = self.project_activities[p.id]
        activity_xblocks = [self._get_activity_xblock(activity.id) for activity in activities]

        result = DottableDict({
            'name': p.name,
            'group_count': len(target_workgroups),
            'organization': p.organization
        })
        if p.organization:
            organization = Organization.fetch(p.organization)
            result.organization_name = organization.display_name

        result.activities = []
        for activity in activities:
            activity_xblock = self._get_activity_xblock(activity.id)
            stage_xblocks = self._v2_get_stage_xblocks(activity_xblock)

            stages_data = OrderedDict((
                (
                    stage_xblock.id,
                    DottableDict({'name': stage_xblock.name,
                                  'deadline': self.format_date_value(stage_xblock.close_date)})
                )
                for stage_xblock in stage_xblocks
            ))

            if not stages_data:
                stages_data[BLANK_V2_STAGE_ID] = {'name': V2_NO_STAGES_AVAILABLE, 'deadline': IRRELEVANT}

            activity_data = DottableDict({
                'name': activity.name,
                'stage_count': len(activity.children),
                'stages': stages_data,
                'grade_type': _("TA Graded") if activity_xblock.ta_graded else _("Peer Graded")
            })
            result.activities.append(activity_data)

        result.workgroups = []
        for workgroup in target_workgroups:
            workgroup_data = self._v2_get_workgroup_data(workgroup, activity_xblocks)
            if workgroup_data:
                workgroup_data.users = self._v2_get_workgroup_users_data(workgroup, activity_xblocks)
                result.workgroups.append(workgroup_data)

        return result


def generate_workgroup_csv_report(course_id, url_prefix, restrict_to_users_ids=None, request=None):
    output_lines = []

    def output_line(line_data_array):
        output_lines.append(','.join(line_data_array))

    wcd = WorkgroupCompletionData(course_id, restrict_to_users_ids=restrict_to_users_ids, request=request)

    # column structure:
    # Group
    # User
    # For each activity
    #   One column per stage in activity

    for project in wcd.build_report_data()["projects"]:
        output_line([project.name])

        activity_names_row = ["", ""]  # Group and User columns
        for activity in project.activities:  # for each activity
            # one column per stage (if no stages are present, fictional NO STAGES is added
            activity_names_row_cells = [""] * len(activity.stages)
            activity_names_row_cells[0] = activity.name
            activity_names_row.extend(activity_names_row_cells)

        output_line(activity_names_row)

        group_header_row = ["Group", ""]  # Group and User columns
        for activity in project.activities:  # for each activity
            for stage_key, stage in activity.stages.items():  # column per stage
                group_header_row.append(stage['name'])

        output_line(group_header_row)

        for workgroup in project.workgroups:
            workgroup_row = [workgroup.name, ""]  # Group and User columns
            for activity_status in workgroup.activity_statuses:  # for each activity
                for stage_key, stage_data in activity_status.stages.items():  # one column per stage
                    if stage_data.get('is_grading_stage', False) and activity_status.ta_graded:
                        stage_status = "TA Graded{} ({})".format(
                            "*" if stage_data.status == "incomplete" else "",
                            "{}{}".format(url_prefix, stage_data.link),
                        )
                    else:
                        stage_status = stage_data['status']

                    workgroup_row.append(stage_status)

            output_line(workgroup_row)

            for user in workgroup.users:
                # apply csv cleaning here
                user_row = ["", user.username]  # Group and User columns
                for user_activity_status in user.activity_statuses:  # for each activity
                    for stage_key, stage in user_activity_status.stages.items():  # one column per stage
                        if not stage.get('is_grading_stage', False) or 'review_groups' not in stage:
                            user_row.append(stage['status'])
                        else:
                            review_group_data = []

                            for review_group in stage.get('review_groups', None):
                                review_group_data.append("{}{} ({})".format(
                                    review_group.name,
                                    "*" if review_group.review_status == "incomplete" else "",
                                    "{}{}".format(url_prefix, review_group.review_link),
                                ))

                            user_row.append('; '.join(review_group_data))
                output_line(user_row)

        output_line("--------")

    return '\n'.join(output_lines)
