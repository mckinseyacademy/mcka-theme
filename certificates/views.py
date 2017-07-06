"""
Views for Certificates djangoapp.
"""
from lib.authorization import permission_group_required
from dateutil.parser import parse as parsedate

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.http import Http404
from django.core.urlresolvers import reverse

from api_client.group_api import PERMISSION_GROUPS
from api_client import user_api, course_api
from admin.views import AccessChecker

from .controller import get_course_certificates_status, get_course_passed_users
from .models import CertificateStatus, CourseCertificateStatus, UserCourseCertificate
from .tasks import generate_course_certificates_task

@require_POST
@permission_group_required(PERMISSION_GROUPS.MCKA_ADMIN, PERMISSION_GROUPS.INTERNAL_ADMIN, PERMISSION_GROUPS.MCKA_SUBADMIN)
def generate_course_certificates(request, course_id):
    """
    Generates certificates for the specified course
    """
    course_end = request.POST.get("course_end", "")
    certificates_status = get_course_certificates_status(
        course_id,
        parsedate(course_end)
    )
    if certificates_status == CertificateStatus.available:
        course_certificate_status = CourseCertificateStatus.objects.create(
            course_id=course_id,
            status = CertificateStatus.generating
        )

        base_domain = request.build_absolute_uri('/')
        generate_course_certificates_task.delay(course_id, base_domain)

    return redirect(reverse('course_details', kwargs={'course_id': course_id}))


def get_certificate_by_uuid(request, certificate_uuid):
    """
    This public view returns HTML representation of the specified certificate
    """
    try:
        certificate = UserCourseCertificate.objects.get(pk=certificate_uuid)
    except UserCourseCertificate.DoesNotExist:
        raise Http404

    user = user_api.get_user(certificate.user_id)
    course = course_api.get_course(certificate.course_id)
    context = {
        'course': course,
        'user': user
    }

    return render(request, "certificates/default_cetificate_template.haml", context)
