from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

class HomeModEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_verification_email(self, user, domain):
        mail_subject = "Activate myCareportal Account"
        message = render_to_string('acc_notify_home_mod_user.html', {
                'user': user,
                'domain': domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        email = EmailMessage(
                    mail_subject, message, self.sender_email, to=[user.email]
        )
        email.send()
