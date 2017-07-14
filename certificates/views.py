"""
Views for Certificates djangoapp.
"""
import urllib

from mimetypes import MimeTypes
from lib.authorization import permission_group_required
from dateutil.parser import parse as parsedate

from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.storage import default_storage
from django.template import RequestContext, Template

from api_client.group_api import PERMISSION_GROUPS
from api_client import user_api, course_api

from .controller import (
    get_course_certificates_status,
    get_certificate_template,
    get_template_asset_path,

)
from .models import (
    CertificateStatus,
    CourseCertificateStatus,
    UserCourseCertificate,
    CertificateTemplateAsset,
    CertificateTemplate,
)
from .tasks import generate_course_certificates_task
from .forms import CertificateTemplateAssetForm, CertificateTemplateForm

@require_POST
@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN
)
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
        CourseCertificateStatus.objects.create(
            course_id=course_id,
            status=CertificateStatus.generating
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
        'course_name': course.name,
        'user_full_name': user.full_name
    }

    custom_template = get_certificate_template(certificate.course_id)
    if custom_template is not None:
        template = Template(custom_template.template)
        context = RequestContext(request, context)
        return HttpResponse(template.render(context))

    return render(
        request,
        "certificates/default_cetificate_template.haml",
        context
    )


@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN
)
def certificate_template_assets(request):
    """
    View for creating and listing certificate template assets
    """
    if request.method == 'POST':
        form = CertificateTemplateAssetForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect(reverse('certificate_template_assets'))
    else:
        form = CertificateTemplateAssetForm()

    template_assets = CertificateTemplateAsset.objects.all()

    return render(request, 'certificates/certificate_template_assets.haml', {
        'form': form,
        'certificate_template_assets': template_assets,
    })


@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN
)
def certificate_templates(request):
    """
    View to list all certificate templates
    """
    templates = CertificateTemplate.objects.all()

    return render(request, 'certificates/certificate_templates.haml', {
        'certificate_templates': templates,
    })


@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN
)
def new_certificate_template(request):
    """
    View for creating new certificate template
    """
    if request.method == 'POST':
        form = CertificateTemplateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('certificate_templates'))
    else:
        form = CertificateTemplateForm()

    return render(request, 'certificates/new_certificate_template.haml', {
        'form': form,
    })


@permission_group_required(
    PERMISSION_GROUPS.MCKA_ADMIN,
    PERMISSION_GROUPS.INTERNAL_ADMIN,
    PERMISSION_GROUPS.MCKA_SUBADMIN
)
def edit_certificate_template(request, template_id):
    """
    View for editing certificate template
    """
    certificate_template = CertificateTemplate.objects.get(id=template_id)
    if request.method == 'POST':
        form = CertificateTemplateForm(
            request.POST,
            instance=certificate_template
        )

        if form.is_valid():
            form.save()
            return redirect(reverse('certificate_templates'))
    else:
        form = CertificateTemplateForm(instance=certificate_template)

    return render(request, 'certificates/new_certificate_template.haml', {
        'form': form,
    })


def load_template_asset(request, asset_id, asset_name): # pylint: disable=unused-argument
    """
    View to locate and return template asset file
    """
    asset_path = get_template_asset_path(asset_id, asset_name)

    if default_storage.exists(asset_path):
        asset = default_storage.open(asset_path).read()
        mime = MimeTypes()
        url = urllib.pathname2url(asset_path)
        mime_type = mime.guess_type(url)
        response = HttpResponse(
            asset, content_type=mime_type[0]
        )
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            asset_name
        )

        return response

    raise Http404
