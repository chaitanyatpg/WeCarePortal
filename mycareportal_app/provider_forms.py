from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re


class UpdateTaskForm(forms.Form):

    comment = forms.CharField(max_length=500, required=False)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super(UpdateTaskForm, self).clean()
        return cleaned_data

class ChooseClientVitalsForm(forms.Form):

    client_email = forms.CharField(max_length=100)
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned_data = super(ChooseClientVitalsForm, self).clean()
        return cleaned_data
