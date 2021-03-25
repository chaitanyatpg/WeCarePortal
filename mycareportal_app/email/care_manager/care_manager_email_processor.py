from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core import mail
from django.core.mail import EmailMessage
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
import datetime

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
    

    def schedule_free_caregiver_email(self,  caregiver_email_address,start_date,end_date,start_hour,start_minute,end_hour,end_minute,subject,caremanager_email, content, user, company):
        #  emailadd ==== to send the email
      
        
        message = render_to_string('schedule_free_caregiver_email.html', {
                'start_date':start_date,
                'end_date' :end_date ,
                'start_hour':start_hour,
                'start_minute':start_minute,

                'end_hour':end_hour,
                'end_minute':end_minute,
                'caregiver_email_address':caregiver_email_address,
                'user': user,
                'content': content,
                'caremanager_email': caremanager_email,
                'company': company
                })
        to_list = []
        to_list_manager = []
        
    
        email = EmailMultiAlternatives(
                    subject, message, from_email = user.email, to=caremanager_email, bcc = caregiver_email_address,

        )
        email.attach_alternative(message, "text/html")
        email.send()




    def send_invoice_mail_by_caremanager(self,user, current_company,client):
    
        subject = "Invoice details"
        message = render_to_string('invoice_email_from_caremanager.html', {
            'user': user,
            'company': current_company,
            })
     
        ccemail = ["mkumar@wecareportal.com"]
        email = email = EmailMultiAlternatives(subject,message,from_email = user.email, to = ccemail)
        
        email.attach_alternative(message, "text/html'")
        email.attach_file('mycareportal_app/download_invoice_pdf/Invoice.pdf')
        email.send()

        


        


