from mycareportal_app.email.email_processor import EmailProcessor
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives

class ClientEmailProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()

    def send_incident_email(self, client, user, care_managers, family_details, provider_details, task, incident, location):
        mail_subject = "Incident reported for {0} {1}".format(client.first_name, client.last_name)
        message = render_to_string('incident_report.html', {
                'client': client,
                'incident': incident,
                'location': location,
                'task':task,
            })
        care_managers = list(filter(lambda x: x.user.incident_emails,care_managers))
        family_details = list(filter(lambda x: x.user.incident_emails,family_details))
        provider_details = list(filter(lambda x: x.user.incident_emails,provider_details))
        to_list = list(map(lambda x: x.email_address, (list(care_managers) + list(family_details) + list(provider_details))))
        to_list.append(user.email)
        email = EmailMultiAlternatives(
                    mail_subject, message, self.sender_email, to=to_list
        )
        email.attach_alternative(message, "text/html")
        email.send()
