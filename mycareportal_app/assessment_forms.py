from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class FindClientForm(forms.Form):

    client_email = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(FindClientForm, self).clean()
        return cleaned_data
