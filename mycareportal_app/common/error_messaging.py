#Handles common error messages
from django.contrib import messages

#Pass in form_errors.as_data() and current request
def render_error_messages(request, form_errors):
    for error in form_errors:
        for message in form_errors[error]:
            for message_text in message:
                messages.error(request, str(message_text))
