"""
Backgroud tasks related to certificates
"""

from celery.decorators import task  # pylint: disable=no-name-in-module, import-error
from celery.utils.log import get_task_logger

from .controller import (
    generate_user_course_certificate,
    get_course_passed_users_list,
    send_certificate_generation_email
)
from .models import CourseCertificateStatus, CertificateStatus

logger = get_task_logger(__name__)  # pylint: disable=invalid-name


@task(name="certificates.generate_course_certificates_task")
def generate_course_certificates_task(course_id, base_domain):
    """
    Generates user course certificate and sends email
    """
    passed_users = get_course_passed_users_list(course_id)
    for user in passed_users:
        if user.complete_status:
            certificate = generate_user_course_certificate(course_id, user)
            try:
                send_certificate_generation_email(
                    course_id,
                    user,
                    certificate.uuid,
                    base_domain
                )
                certificate.email_sent = True
                certificate.save()
            except Exception as ex:  # pylint: disable=broad-except
                logger.exception(
                    'An error occurred while generating certificate: %s',
                    ex.message
                )

    # certificate generation task completed update course certs status
    course_certificate_status = CourseCertificateStatus.objects.get(
        course_id=course_id
    )
    course_certificate_status.status = CertificateStatus.generated
    course_certificate_status.save()
