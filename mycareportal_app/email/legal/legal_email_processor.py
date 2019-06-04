from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

class LegalEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_incident_email(self, incident_report, care_managers):
        # mail_subject = "Incident reported for {0} {1}".format(client.first_name, client.last_name)
        mail_subject = "Legal Help Request [Do Not reply System Generated Email]"
        message = render_to_string('legal_incident_report.html', {
                'client': incident_report.client,
                'incident': incident_report.incident,
                'location': incident_report.location,
                'task':incident_report.task,
                'reporter':incident_report.reporter,
                'care_managers':care_managers
            })
        to_list = []
        # Currently hard coded values - will update with values from admin portal later
        to_list.append("mkumar@wecareportal.com")
        to_list.append("dranjan@wecareportal.com")
        #to_list.append("dhruv.ranjan@gmail.com")
        email = EmailMultiAlternatives(
                    mail_subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()

    def send_generic_legal_email(self, client, subject, content, user, company):
        message = render_to_string('generic_legal_email.html', {
            'client': client,
            'content': content,
            'user': user,
            'company': company
        })
        to_list = []
        #to_list.append("mkumar@wecareportal.com")
        #to_list.append("dranjan@wecareportal.com")
        to_list.append("dhruv.ranjan@gmail.com")
        email = EmailMultiAlternatives(
                    subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()
