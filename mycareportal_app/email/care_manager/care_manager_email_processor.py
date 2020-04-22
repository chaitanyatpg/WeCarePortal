from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core import mail
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives

class CareManagerEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_verification_email(self, user, domain):
        mail_subject = "Activate myCareportal Account"
        message = render_to_string('acc_notify_care_manager.html', {
                'user': user,
                'domain': domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        email = EmailMessage(
                    mail_subject, message, self.sender_email, to=[user.email]
        )
        email.send()

    def new_send_verification_email(self, user, domain):
        mail_subject = "Activate myCareportal Account"
        message = render_to_string('acc_notify_new_care_manager.html', {
                'user': user,
                'domain': domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
        email = EmailMessage(
                    mail_subject, message, self.sender_email, to=[user.email]
        )
        email.send()
    

    def schedule_free_caregiver_email(self,  caregiver_email_address,subject, content, user, company):
        #  emailadd ==== to send the email
        connection = mail.get_connection() 
        
        message = render_to_string('schedule_free_caregiver_email.html', {
                
                'caregiver_email_address':caregiver_email_address,
                'user': user,
                'content': content,
                # 'caregiver':caregiver, 
                # 'caregiver.last_name': caregiver.last_name,
                'company': company
                })
        to_list = []
        to_list_manager = []

        to_list_manager.append(user.username)
        email = EmailMultiAlternatives(
                    subject, message, self.sender_email,  to=to_list_manager, bcc = caregiver_email_address, connection=connection

        )
        email.attach_alternative(message, "text/html")
        email.send()

        connection.close()


