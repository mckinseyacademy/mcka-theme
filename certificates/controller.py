"""
Core logic to sanitise information for certificate views
"""

import os
import urlparse

from datetime import datetime
from django.conf import settings
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.urlresolvers import reverse

from courses.models import FeatureFlags
from api_client import course_api
from admin.controller import get_internal_courses_list

from .models import (
    CourseCertificateStatus,
    CertificateStatus,
    UserCourseCertificate,
    CertificateTemplate
)


def get_course_certificates_status(course_id, course_end_date):
    """
    Returns course certificates status given course id and course end date
    """
    try:
        features = FeatureFlags.objects.get(course_id=course_id)
    except FeatureFlags.DoesNotExist:
        return CertificateStatus.notavailable

    if features.certificates and course_end_date <= datetime.now():
        try:
            course_certificate_status = CourseCertificateStatus.objects.get(
                course_id=course_id
            )
            return course_certificate_status.status
        except CourseCertificateStatus.DoesNotExist:
            return CertificateStatus.available

    return CertificateStatus.notavailable


def get_course_passed_users_list(course_id):
    """
    Returns list of all users who have passed the course
    """
    passed_users_result_set = []
    passed_users_page_one = course_api.get_course_passed_users(course_id)

    passed_users_result_set.extend(passed_users_page_one.results)
    for page_num in xrange(2, passed_users_page_one.num_pages + 1):
        passed_users_result_set.extend(
            course_api.get_course_passed_users(course_id, page_num).results
        )

    return passed_users_result_set


def generate_user_course_certificate(course_id, user):
    """
    Creates user course certificate record for the specified course and user
    """
    certificate = UserCourseCertificate.objects.create(
        course_id=course_id,
        user_id=user.id
    )

    return certificate


def get_certificate_url(base_domain, certificate_uuid):
    """
    Helper method to generate certificates url from uuid and base domain
    """
    certificate_path = reverse(
        'get_certificate_by_uuid',
        kwargs={'certificate_uuid': certificate_uuid}
    )

    return  urlparse.urljoin(base_domain, certificate_path)


def send_certificate_generation_email(
        course_id, # pylint: disable=unused-argument
        user,
        certificate_uuid,
        base_domain
    ):
    """
    Send certificate generated email notification
    """
    context = {
        'username': user.username,
        'email': user.email,
        'certificate_link': get_certificate_url(base_domain, certificate_uuid),
    }
    email_html = loader.render_to_string(
        'certificates/course_certificate_notification_email.haml',
        context
    )
    email_plain = strip_tags(email_html)

    email = EmailMultiAlternatives(
        settings.CERTIFICATES_EMAIL_SUBJECT,
        email_plain,
        settings.APROS_EMAIL_SENDER,
        [user.email],
        headers={'Reply-To': settings.APROS_EMAIL_SENDER}
    )
    email.attach_alternative(email_html, "text/html")
    email.send(fail_silently=False)


def get_certificate_template(course_id):
    """
    Retrieves the certificate template based on course_id
    """
    try:
        template = CertificateTemplate.objects.get(
            course_id=course_id,
        )
    except CertificateTemplate.DoesNotExist:
        return None

    return template


def get_courses_choice_list(request=None):
    """
    Returns list of all courses for course choices in certificate template
    """
    if request and request.user.is_internal_admin:
        course_choice_list = [
            (course.course_id, course.display_name)
            for course in get_internal_courses_list()
        ]
    else:
        course_choice_list = [
            (course.id, course.name)
            for course in course_api.get_course_list()
        ]

    return course_choice_list


def get_template_asset_path(asset_id, asset_name):
    """
    Helper method to build template asset path from asset id and name
    """
    return os.path.join(
        settings.BASE_CERTIFICATE_TEMPLATE_ASSET_PATH,
        asset_id,
        asset_name
    )
