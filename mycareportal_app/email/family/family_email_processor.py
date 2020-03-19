from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

class FamilyEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_verification_email(self, user, domain):
        mail_subject = "Activate myCareportal Account"
        message = render_to_string('acc_notify_family.html', {
                'user': user,
                'domain': domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        email = EmailMessage(
                    mail_subject, message, self.sender_email, to=[user.email]
        )
        email.send()

    def send_family_email(self, family_contact, subject, content, user, company):
        message = render_to_string('send_family_email.html', {
                'familycontact': family_contact,
                'content': content,
                'user': user,
                'company': company
                })
        to_list = []
        #to_list.append("mkumar@wecareportal.com")
        #to_list.append("dranjan@wecareportal.com")
        #to_list.append("dhruv.ranjan@gmail.com")
        #to_list.append(company.attorney_email)
        to_list.append(family_contact.email_address)
        email = EmailMultiAlternatives(
                    subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()
