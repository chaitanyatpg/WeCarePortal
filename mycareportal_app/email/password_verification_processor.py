
from email_processor import EmailProcessor
from mycareportal_app.common import tokens as tokens

class PasswordVerificationProcessor(EmailProcessor):

    def __init__(self):
        super().__init__()
