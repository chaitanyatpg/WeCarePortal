from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class CaregiverRegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    date_of_birth = forms.DateTimeField()
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    password = forms.CharField(max_length=30)
    confirm_password = forms.CharField(max_length=30)
    ssn = forms.IntegerField()
    referrer = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('Image file type is not recognized. Please try again')
        return picture

    def clean(self):

        cleaned_data = super(CaregiverRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class CaregiverEditForm(forms.Form):

    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1, required=False)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=2, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    date_of_birth = forms.DateTimeField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200, required=False)
    ssn = forms.IntegerField(required=False)
    referrer = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('Image file type is not recognized. Please try again')
        return picture

    def clean(self):

        cleaned_data = super(CaregiverEditForm, self).clean()
        return cleaned_data

class FindCaregiverForm(forms.Form):

    caregiver_email = forms.CharField(max_length=100)

    def clean(self):

        cleaned_data = super(FindCaregiverForm, self).clean()
        return cleaned_data

class UpdateTaskForm(forms.Form):

    comment = forms.CharField(max_length=500)
    status = forms.CharField(max_length=50)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super(UpdateTaskForm, self).clean()
        return cleaned_data
