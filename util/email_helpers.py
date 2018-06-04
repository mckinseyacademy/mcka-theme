"""
email helper methods
"""
from django.template import loader
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_html_email(
    subject='', to_emails=[],
    from_email=settings.APROS_EMAIL_SENDER,
    reply_to=[settings.MCKA_SUPPORT_EMAIL],
    template_name=None, template_data=None
):
    """
    helper method for sending out html emails
    """
    if not to_emails:
        raise ValueError('To emails is a required param')

    if template_name:
        html_content = loader.render_to_string(
            template_name,
            template_data or {}
        )
        text_content = strip_tags(html_content)
    else:
        raise ValueError('Please provide an email template (path or name)')

    email = EmailMultiAlternatives(
        subject, text_content, from_email, to_emails,
        reply_to=reply_to
    )

    email.content_subtype = "html"
    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)
