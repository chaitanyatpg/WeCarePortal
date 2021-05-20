from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re

class CaregiverRegistrationForm(forms.Form):

    MIN_LENGTH = 8
    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    other_state_name = forms.CharField(max_length=100,required=False)
    zip_code = forms.CharField(max_length=10)
    date_of_birth = forms.DateTimeField()
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    ssn = forms.CharField(max_length=20, required=False)
    referrer = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)
    notes = forms.CharField(max_length=1000, required=False)

    def clean_picture(self):
        try:
            picture = self.cleaned_data['profile_picture']
            if picture:
                if picture._size > self.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')
        except KeyError:
            val = ""
            # raise forms.ValidationError('Formats supported JPEG, PNG, JPG')
        #picture = self.cleaned_data['profile_picture']
        #if not picture:
        #    return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('Image file type is not recognized. Please try again')
        #return picture

    def clean(self):

        cleaned_data = super(CaregiverRegistrationForm, self).clean()
        self.clean_picture()
        return cleaned_data

class CaregiverEditForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1, required=False)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    other_state_name = forms.CharField(max_length=100,required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    date_of_birth = forms.DateTimeField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200, required=False)
    ssn = forms.CharField(max_length=20, required=False)
    referrer = forms.CharField(max_length=100, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)
    rating = forms.IntegerField(required=False)
    hourly_rate = forms.IntegerField(required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)
    notes = forms.CharField(max_length=1000, required=False)

    def clean_picture(self):
        
        try:
            picture = self.cleaned_data['profile_picture']
            if picture:
                if picture._size > self.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')
        except KeyError:
            val = ""
            # raise forms.ValidationError('Formats supported JPEG, PNG, JPG')
        #picture = self.cleaned_data['profile_picture']
        #if not picture:
        #    return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('Image file type is not recognized. Please try again')
        #return picture

    def clean(self):

        cleaned_data = super(CaregiverEditForm, self).clean()
        self.clean_picture()
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
    template_entries = forms.CharField(max_length=500, required=False)

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
    monday = forms.BooleanField(required=False)
    tuesday = forms.BooleanField(required=False)
    wednesday = forms.BooleanField(required=False)
    thursday = forms.BooleanField(required=False)
    friday = forms.BooleanField(required=False)
    saturday = forms.BooleanField(required=False)
    sunday = forms.BooleanField(required=False)
    frequency = forms.CharField(max_length=100)
    live_in = forms.BooleanField(required=False)




    def clean(self):
        cleaned_data = super(ScheduleShiftForm, self).clean()
        return cleaned_data

class ScheduleShiftFreeCaregiverForm(forms.Form):

    start_date = forms.DateField()
    end_date = forms.DateField()
    start_hour = forms.CharField(max_length=10)
    start_minute = forms.CharField(max_length=10)
    end_hour = forms.CharField(max_length=10)
    end_minute = forms.CharField(max_length=10)
    # caregiver_id = forms.IntegerField()
    subject = forms.CharField(max_length=100)
    content = forms.CharField(max_length=1000)


    def clean(self):
        cleaned_data = super(ScheduleShiftFreeCaregiverForm, self).clean()
        return cleaned_data

    def __len__(self):
        return len(self.ScheduleShiftFreeCaregiverForm)

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

class CaregiverPayrollForm(forms.Form):


    weekend_hourly_rate = forms.DecimalField(required=False)
    holiday_hourly_rate = forms.DecimalField(required=False)
    weekend_holiday_rate =forms.DecimalField(required=False)
    live_in_rate =forms.DecimalField(required=False)
    weekend_live_in_rate = forms.DecimalField(required=False)
    holiday_live_in_rate =forms.DecimalField(required=False)
    weekend_holiday_live_in_rate = forms.DecimalField(required=False)
    caregiver_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(CaregiverPayrollForm, self).clean()
        return cleaned_data
        
class UpdateAdminManageTaskForm(forms.Form):

    comment = forms.CharField(max_length=500, required=False)
    status = forms.CharField(max_length=50)
    task_id = forms.IntegerField()
    client_id = forms.IntegerField()
    

    def clean(self):
        cleaned_data = super(UpdateAdminManageTaskForm, self).clean()
        return cleaned_data