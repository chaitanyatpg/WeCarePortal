from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re

class CaregiverRegistrationForm(forms.Form):

    MIN_LENGTH = 8

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
    ssn = forms.CharField(max_length=20)
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
        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if (not(bool(re.match("(?=.*[A-Z])",password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if (not(bool(re.search(r'\d',password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
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
    ssn = forms.CharField(max_length=20)
    referrer = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)
    rating = forms.IntegerField(required=False)

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

    comment = forms.CharField(max_length=500, required=False)
    status = forms.CharField(max_length=50)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='', required=False)
    incident_id = forms.IntegerField(required=False)
    location_id = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super(UpdateTaskForm, self).clean()
        return cleaned_data

class ScheduleShiftForm(forms.Form):

    caregiver_id = forms.IntegerField()
    client_id = forms.IntegerField()
    start_date = forms.DateField()
    end_date = forms.DateField()
    start_hour = forms.CharField(max_length=10)
    start_minute = forms.CharField(max_length=10)
    end_hour = forms.CharField(max_length=10)
    end_minute = forms.CharField(max_length=10)

    def clean(self):
        cleaned_data = super(ScheduleShiftForm, self).clean()
        return cleaned_data

class EditScheduleForm(forms.Form):

    schedule_id = forms.IntegerField()
    caregiver_id = forms.IntegerField()
    start_hour = forms.CharField(max_length=10)
    start_minute = forms.CharField(max_length=10)
    end_hour = forms.CharField(max_length=10)
    end_minute = forms.CharField(max_length=10)

    def clean(self):
        cleaned_data = super(EditScheduleForm, self).clean()
        return cleaned_data

class DeleteScheduleForm(forms.Form):

    schedule_id = forms.IntegerField()
    caregiver_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super(DeleteScheduleForm, self).clean()
        return cleaned_data
