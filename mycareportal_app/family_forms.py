from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re

class UpdateTaskForm(forms.Form):
    comment = forms.CharField(max_length=500, required=False)
    sign_off = forms.BooleanField(required=False)
    # status = forms.CharField(max_length=50)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()
    # new  for file upload
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='', required=False)
    # new  for file upload
    template_entries = forms.CharField(max_length=500, required=False)
    # incident_id = forms.IntegerField(required=False)
    # location_id = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(UpdateTaskForm, self).clean()
        return cleaned_data



class LegalEmailFamilyForm(forms.Form):

    familycontact_uid = forms.UUIDField()
    subject = forms.CharField(max_length=100)
    content = forms.CharField(max_length=1000)

    def clean(self):
        cleaned_data = super(LegalEmailFamilyForm, self).clean()
        return cleaned_data

class FindFamilyContactForm(forms.Form):
    
    family_email = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(FindFamilyContactForm, self).clean()
        return cleaned_data