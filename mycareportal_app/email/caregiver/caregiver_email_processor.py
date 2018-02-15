from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

class CaregiverEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_verification_email(self, user, domain):
        mail_subject = "Activate myCareportal Account"
        message = render_to_string('acc_notify_caregiver.html', {
                'user': user,
                'domain': domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        email = EmailMessage(
                    mail_subject, message, self.sender_email, to=[user.email]
        )
        email.send()

    def send_clock_in_email(self, client, caregiver, care_managers, family_members, clock_in_timestamp):
        mail_subject = "Caregiver {0} {1} clocked in for client {2} {3}".format(
            caregiver.first_name, caregiver.last_name, client.first_name, client.last_name)
        message = render_to_string('clock_in_report.html', {
                'client': client,
                'caregiver': caregiver,
                'timestamp': clock_in_timestamp
            })
        to_list = list(map(lambda x: x.email_address, (list(care_managers) + list(family_members))))
        email = EmailMultiAlternatives(
                    mail_subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()

    def send_clock_out_email(self, client, caregiver, care_managers, family_members, clock_out_timestamp):
        mail_subject = "Caregiver {0} {1} clocked out for client {2} {3}".format(
            caregiver.first_name, caregiver.last_name, client.first_name, client.last_name)
        message = render_to_string('clock_out_report.html', {
                'client': client,
                'caregiver': caregiver,
                'timestamp': clock_out_timestamp
            })
        to_list = list(map(lambda x: x.email_address, (list(care_managers) + list(family_members))))
        email = EmailMultiAlternatives(
                    mail_subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()
