from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext as _

def sendMultipleEmails(messages):
    connection = mail.get_connection()
    connection.open()
    for message in messages:
        try:
            message.send()
        except BadHeaderError, e:
            connection.close()
            return e
    connection.close()
    return True

def email_add_active_student(request, program, student):
    subject, from_email, to = 'Welcome to the {} Program!'.format(program.display_name), settings.ENROLL_STUDENT_EMAIL, student.email
    date_format = _('%m/%d/%Y')
    url = '/courses/{}/lessons'.format(program.courses[0].course_id)
    text_content = 'Welcome to the {} Program! Your program starts on {}. Open link below to see the program overview. {}'.format(
        program.display_name, program.start_date.strftime(date_format), request.build_absolute_uri(url))
    html_content = '<h2>Welcome to the {} Program!</h2><p>Your program starts on {}. <a href="{}">Click here</a> to see the program overview.</p>'.format(
        program.display_name, program.start_date.strftime(date_format), request.build_absolute_uri(url))
    msg = EmailMultiAlternatives(
        subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.attach_alternative(text_content, "text/plain")
    return msg

def email_add_inactive_student(request, program, student):
    subject, from_email, to = 'Welcome to the {} Program!'.format(program.display_name), settings.ENROLL_STUDENT_EMAIL, student.email
    date_format = _('%m/%d/%Y')
    url = '/accounts/activate/{}'.format(
                        student.activation_code
                    )
    text_content = 'Welcome to the {} Program! Your program starts on {}. Open link below to register a user account and get started. {}'.format(
        program.display_name, program.start_date.strftime(date_format), request.build_absolute_uri(url))
    html_content = '<h2>Welcome to the {} Program!</h2><p>Your program starts on {}. <a href="{}">Click here</a> to register a user account and get started.</p>'.format(
        program.display_name, program.start_date.strftime(date_format), request.build_absolute_uri(url))
    msg = EmailMultiAlternatives(
        subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.attach_alternative(text_content, "text/plain")
    return msg
