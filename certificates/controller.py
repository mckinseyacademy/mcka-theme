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
from api_client import course_api, user_api

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
    features = FeatureFlags.objects.get(course_id=course_id)
    if features.certificates and course_end_date <= datetime.now():
        try:
            course_certificate_status = CourseCertificateStatus.objects.get(
                course_id=course_id
            )
            return course_certificate_status.status
        except CourseCertificateStatus.DoesNotExist:
            return CertificateStatus.available

    return CertificateStatus.notavailable


def get_course_passed_users(course_id):
    """
    Returns list of users who have passed the course
    """
    # TODO: this is a temporary measure until we finalize what user data is
    # needed in certificate email. Once we finalize then
    # get_course_passed_users_id_list api should return passed users info not
    # just ids, so we don't need to make seperate api call to get passed users
    # info.

    passed_user_ids = map(
        str, course_api.get_course_passed_users_id_list(course_id)
    )
    passed_users = user_api.get_users(ids=passed_user_ids)

    return passed_users


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


def get_courses_choice_list():
    """
    Returns list of all courses for course choices in certificate template
    """
    courses = course_api.get_course_list()
    return [(course.id, course.name) for course in courses]


def get_template_asset_path(asset_id, asset_name):
    """
    Helper method to build template asset path from asset id and name
    """
    return os.path.join(
        settings.BASE_CERTIFICATE_TEMPLATE_ASSET_PATH,
        asset_id,
        asset_name
    )
