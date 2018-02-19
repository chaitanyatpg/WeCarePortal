from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class EmailSettingsForm(forms.Form):

    incident_emails = forms.BooleanField(required=False)
    clock_in_emails = forms.BooleanField(required=False)
    clock_out_emails = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super(EmailSettingsForm, self).clean()
        return cleaned_data
