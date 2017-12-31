from django.core.mail import send_mail
from django.core.mail import EmailMessage

class EmailProcessor:

    #email address of sender
    sender_email = "info@wecareportal.com"

    def send_simple_email(self, to_email, message, subject):
        #send_mail('Test sendgrid', 'Test message', 'info@wecareportal.com', ['dhruv.ranjan@gmail.com'], fail_silently=False)
        send_email(subject,
                    message,
                    self.sender_email,
                    [to_email],
                    fail_silently=False)

    def send_simple_group_email(self, to_emails, message, subject):
        data_tuples = self.construct_email_tuples(to_emails,message_subject)
        send_mass_email(data_tuples)

    def construct_email_tuples(self, to_emails, message, subject):
        data_list = []
        for i in to_emails:
            current_tuple = (subject,
                            message,
                            self.sender_email,
                            [to_email])
            data_list.append(current_tuple)
        data_tuples = tuple(data_list)
        return data_tuples
