from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage

class AdminEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_company_sign_up_email(self, user, domain):
        mail_subject = "Notification: Company Sign Up"
        message = render_to_string('notify_company_sign_up.html', {
                'user': user
        })
        to_list = ['dhruv.ranjan@gmail.com','dranjan@wecareportal.com','lewald@wecareportal.com']
        email = EmailMessage(
                    mail_subject, message, self.sender_email,to=to_list
        )
        email.send()
