from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class UpdateTaskForm(forms.Form):

    comment = forms.CharField(max_length=500, required=False)
    #status = forms.CharField(max_length=50)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()
    #attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='', required=False)
    #incident_id = forms.IntegerField(required=False)
    #location_id = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(UpdateTaskForm, self).clean()
        return cleaned_data
