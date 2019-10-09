from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.utils.translation import ugettext as _
from util.email_helpers import send_html_email
from urllib.parse import urljoin


def sendMultipleEmails(messages):
    connection = mail.get_connection()
    connection.open()
    for message in messages:
        try:
            message.send()
        except BadHeaderError as e:
            connection.close()
            return e
    connection.close()
    return True


def email_add_active_student(request, program, student):
    subject, from_email, to = _('Welcome to the {display_name} Program!').format(
        display_name=program.display_name), settings.ENROLL_STUDENT_EMAIL, student.email
    date_format = _('%m/%d/%Y')
    url = '/courses/{}/lessons'.format(program.courses[0].course_id)
    text_content = _('Welcome to the {display_name} Program! Your program starts on '
                     '{date}. Open link below to see the program overview. {url}').format(
        display_name=program.display_name,
        date=program.start_date.strftime(date_format),
        url=request.build_absolute_uri(url)
    )

    html_content = _('{html_h2}Welcome to the {display_name} Program!{html_h2_end}'
                     'Your program starts on {date}. {html_anchor_start}Click here '
                     '{html_anchor_end} to see the program overview.{html_p_end}').format(
        html_h2='<h2>',
        display_name=program.display_name,
        html_h2_end='</h2><p>',
        date=program.start_date.strftime(date_format),
        html_anchor_start='<a href = '+str(request.build_absolute_uri(url))+'>',
        html_anchor_end='</a>',
        html_p_end='</p>'
    )

    msg = EmailMultiAlternatives(
        subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.attach_alternative(text_content, "text/plain")
    return msg


def email_add_inactive_student(request, program, student):

    subject, from_email, to = _('Welcome to the {display_name} Program!').format(
        display_name=program.display_name), settings.ENROLL_STUDENT_EMAIL, student.email

    date_format = _('%m/%d/%Y')
    url = '/accounts/activate/{}'.format(
                        student.activation_code
                    )
    text_content = _('Welcome to the {display_name} Program! Your program starts on {date}. '
                     'Open link below to register a user account and get started. {url}').format(
        display_name=program.display_name,
        date=program.start_date.strftime(date_format),
        url=request.build_absolute_uri(url)
    )

    html_content = _('{html_h2}Welcome to the {display_name} Program!{html_h2_end} '
                     'Your program starts on {date}.{html_anchor_start}Click here '
                     '{html_anchor_end} to register a user account '
                     'and get started.{html_p_end}').format(
        html_h2='<h2>',
        display_name=program.display_name,
        html_h2_end='</h2><p>',
        date=program.start_date.strftime(date_format),
        html_anchor_start='<a href = ' + str(request.build_absolute_uri(url)) + '>',
        html_anchor_end='</a>',
        html_p_end='</p>'
    )

    msg = EmailMultiAlternatives(
        subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.attach_alternative(text_content, "text/plain")
    return msg


def email_add_single_new_user(absolute_activation_uri, student, activation_record):

    subject, from_email, to = _('Mckinsey academy activation mail!'), settings.ENROLL_STUDENT_EMAIL, student.email
    url = '{}'.format(activation_record.activation_key)

    text_content = _("Welcome to the Mckinsey academy! An administrator has created an "
                     "account on McKinsey Academy for your use. To activate your account,"
                     " please copy and paste this address into your web browser's "
                     "address bar: {uri}/{url}").format(
        uri=absolute_activation_uri,
        url=url
    )

    html_content = _("{html_h2}Welcome to the Mckinsey academy!{html_h2_end}"
                     "An administrator has created an account on McKinsey Academy "
                     "for your use. To activate your account, please {html_anchor_start}"
                     " Click here{html_anchor_end} to register a user account "
                     "and get started.{html_p_end}").format(
        html_h2='<h2>',
        html_h2_end='</h2><p>',
        html_anchor_start='<a href='+str(absolute_activation_uri)+'/'+str(url)+'>',
        html_anchor_end='</a>',
        html_p_end='</p>'
    )
    msg = EmailMultiAlternatives(
        subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.attach_alternative(text_content, "text/plain")
    return msg


def create_multiple_emails(from_email, to_email_list, subject, email_body):
    from django.utils.html import strip_tags
    text_content = strip_tags(email_body)
    html_content = email_body
    msg = EmailMultiAlternatives(
        subject, text_content, from_email, to_email_list)
    msg.content_subtype = "html"
    msg.attach_alternative(html_content, "text/html")
    return msg


def email_user_activation_link(request, user_data, activation_link):

    subject = _('Welcome to McKinsey Academy')
    template = 'accounts/user_activation_email.haml'
    mcka_logo = urljoin(
        base=request.build_absolute_uri(),
        url='/static/image/mcka_email_logo.png'
    )

    send_html_email(
        subject=subject,
        to_emails=[user_data.get('email')], template_name=template,
        template_data={
            'first_name': user_data.get('first_name'),
            'activation_link': activation_link, 'support': settings.MCKA_SUPPORT_FORM_LINK,
            'mcka_logo_url': mcka_logo,
        }
    )
