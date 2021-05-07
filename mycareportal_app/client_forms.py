from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re
import datetime

class ClientRegistrationForm(forms.Form):

    # Limit uploads to 5MB
    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1)
    date_of_birth = forms.DateTimeField()
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    other_state_name = forms.CharField(max_length=100,required=False)
    zip_code = forms.CharField(max_length=10)
    time_zone = forms.CharField(max_length=50)
    profile_picture = forms.ImageField(label='Select file', required=False)
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)
    referrer = forms.CharField(max_length=100, required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)
    notes = forms.CharField(max_length=1000, required=False)
    is_caregiver = forms.BooleanField(required=False)


    def clean_picture(self):
        
        try:
            picture = self.cleaned_data['profile_picture']
            if picture:
                if picture._size > self.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')
        except KeyError:
            raise forms.ValidationError('Formats supported JPEG, PNG, JPG')
        #if not picture:
        #    return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('Image file type is not recognized. Please try again')
        #return picture

    def clean(self):
        
        cleaned_data = super(ClientRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        self.clean_picture()
        return cleaned_data

    

class EditClientDetailsForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1)
    date_of_birth = forms.DateTimeField()
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    other_state_name = forms.CharField(max_length=100,required=False)
    zip_code = forms.CharField(max_length=50)
    time_zone = forms.CharField(max_length=50)
    profile_picture = forms.ImageField(label='Select file', required=False)
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)
    referrer = forms.CharField(max_length=100, required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)
    notes = forms.CharField(max_length=1000, required=False)

    def clean_picture(self):
        print("self.cleaned_dataself.cleaned_data",self.cleaned_data)
        # if self.cleaned_data['profile_picture']:
        try:
            picture = self.cleaned_data['profile_picture']
            if picture:
                if picture._size > self.MAX_UPLOAD_SIZE:
                    raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')
        #picture = self.cleaned_data['profile_picture']
        except KeyError:
            raise forms.ValidationError('Formats supported JPEG, PNG, JPG')
            
        # if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('Image file type is not recognized. Please try again')
        # return picture

    def clean(self):
        cleaned_data = super(EditClientDetailsForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        self.clean_picture()
        return cleaned_data

class FamilyDetailsForm(forms.Form):

    MIN_LENGTH = 8
    MAX_UPLOAD_SIZE = 5242880

    client_email = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    relationship = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    power_of_attorney = forms.BooleanField(required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)
    family_id = forms.IntegerField(required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if picture:
            if picture._size > self.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')
        #picture = self.cleaned_data['profile_picture']
        #if not picture:
        #    return None
        #if not picture.content_type or not picture.content_type.startswith('image'):
        #    raise forms.ValidationError('Image file type is not recognized. Please try again')
        #return picture

    def clean(self):
        cleaned_data = super(FamilyDetailsForm, self).clean()
        self.clean_picture()
        return cleaned_data

class DeleteFamilyDetailsForm(forms.Form):

    family_id = forms.IntegerField()
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(DeleteFamilyDetailsForm, self).clean()
        return cleaned_data

class ProviderDetailsForm(forms.Form):

    MIN_LENGTH = 8

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    #provider_type = forms.CharField(max_length=100)
    speciality = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    provider_id = forms.IntegerField(required=False)
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(ProviderDetailsForm, self).clean()
        return cleaned_data

class DeleteProviderDetailsForm(forms.Form):

    provider_id = forms.IntegerField()
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(DeleteProviderDetailsForm, self).clean()
        return cleaned_data

class PharmacyDetailsForm(forms.Form):

    pharmacy_name = forms.CharField(max_length=100)
    contact_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    fax_number = forms.CharField(max_length=50, required=False)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    pharmacy_id = forms.IntegerField(required=False)
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(PharmacyDetailsForm, self).clean()
        return cleaned_data

class DeletePharmacyDetailsForm(forms.Form):

    pharmacy_id = forms.IntegerField()
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(DeletePharmacyDetailsForm, self).clean()
        return cleaned_data

class PayerDetailsForm(forms.Form):

    payer_name = forms.CharField(max_length=100)
    contact_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    fax_number = forms.CharField(max_length=50, required=False)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    policy_start_date = forms.DateField()
    policy_end_date = forms.DateField()
    policy_number = forms.CharField(max_length=40)
    payer_id = forms.IntegerField(required=False)
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(PayerDetailsForm, self).clean()
        return cleaned_data

class DeletePayerDetailsForm(forms.Form):

    payer_id = forms.IntegerField()
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(DeletePayerDetailsForm, self).clean()
        return cleaned_data

class FindCaregiverForm(forms.Form):

    client_email = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(FindCaregiverForm, self).clean()
        return cleaned_data

class AssignCaregiverForm(forms.Form):

    caregiver_email = forms.CharField(max_length=100)
    client_email = forms.CharField(max_length=100)
    is_unassign = forms.CharField(initial="False", required=False)

    def clean(self):
        cleaned_data = super(AssignCaregiverForm, self).clean()
        return cleaned_data

class CreateTaskForm(forms.Form):

    activity_master = forms.CharField(max_length=100)
    sub_category = forms.CharField(max_length=100)
    task = forms.CharField(max_length=300)

    def clean(self):
        cleaned_data = super(CreateTaskForm, self).clean()
        return cleaned_data

class AssignTaskForm(forms.Form):

    MAX_TASK_DURATION = 365
    MAX_FILE_SIZE = 104857600 #100mb in bytes

    client_email = forms.CharField(max_length=200)
    task = forms.CharField(max_length=300)
    task_type = forms.CharField(max_length=100)
    monday = forms.BooleanField(required=False)
    tuesday = forms.BooleanField(required=False)
    wednesday = forms.BooleanField(required=False)
    thursday = forms.BooleanField(required=False)
    friday = forms.BooleanField(required=False)
    saturday = forms.BooleanField(required=False)
    sunday = forms.BooleanField(required=False)
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    start_hour = forms.CharField(required=False)
    start_minute = forms.CharField(required=False)
    end_hour = forms.CharField(required=False)
    end_minute = forms.CharField(required=False)
    description = forms.CharField(required=False, max_length=1000)
    link = forms.CharField(required=False, max_length=500)
    #attachment = forms.FileField(label='Select file', required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)
    template = forms.UUIDField(required=False)
    alert_active = forms.BooleanField(required=False)
    #def clean_attachment(self):
    #    attachments = self.cleaned_data.get('attachment')
    #    for attachment in attachments:
    #        print(attachment)
    #        if attachment.size > self.MAX_FILE_SIZE:
    #            raise forms.ValidationError("Attachment size must be less than 100mb")

    def clean_date_duration(self, start_date, end_date):
        duration = end_date - start_date
        print(duration.days)
        if duration.days > 365:
            raise forms.ValidationError("Tasks can only be assigned for a maximum duration of one year".
                                        format(self.MAX_TASK_DURATION))


    def clean(self):
        cleaned_data = super(AssignTaskForm, self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        self.clean_date_duration(start_date, end_date)
        #self.clean_attachment()
        return cleaned_data

class FindClientForm(forms.Form):

    client_email = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(FindClientForm, self).clean()
        return cleaned_data

class EditTaskForm(forms.Form):

    client_id = forms.IntegerField()
    task_id = forms.IntegerField()
    start_hour = forms.CharField(max_length=2, required=False)
    start_minute = forms.CharField(max_length=2, required=False)
    end_hour = forms.CharField(max_length=2, required=False)
    end_minute = forms.CharField(max_length=2, required=False)
    description = forms.CharField(max_length=1000, required=False)
    link = forms.CharField(max_length=500, required=False)
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='Select files', required=False)

    def clean(self):
        cleaned_data = super(EditTaskForm, self).clean()
        return cleaned_data

class DeleteTaskForm(forms.Form):

    task_id = forms.IntegerField()

    def clean(self):
        cleaned_data = super(DeleteTaskForm, self).clean()
        return cleaned_data

class RegisterClientTabletForm(forms.Form):

    client_id = forms.IntegerField()
    tablet_id = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(RegisterClientTabletForm, self).clean()
        return cleaned_data

class LegalEmailForm(forms.Form):

    client_uid = forms.UUIDField()
    subject = forms.CharField(max_length=100)
    content = forms.CharField(max_length=1000)

    def clean(self):
        cleaned_data = super(LegalEmailForm, self).clean()
        return cleaned_data

class DeactivateClientForm(forms.Form):

    client_uid = forms.UUIDField()

    def clean(self):
        cleaned_data = super(DeactivateClientForm, self).clean()
        return cleaned_data

class EndOfLifeForm(forms.Form):

    comment = forms.CharField(max_length=500, required=False)
    end_of_life_id = forms.IntegerField()
    client_id = forms.IntegerField()
    attachment = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), label='', required=False)

    def clean(self):
        cleaned_data = super(EndOfLifeForm, self).clean()
        return cleaned_data



class CopyAssignTaskForm(forms.Form):
    clientwithtask = forms.CharField(max_length=500)
    clientwithouttask = forms.CharField(max_length=500)
    def clean(self):
        cleaned_data = super(CopyAssignTaskForm, self).clean()
        return cleaned_data


class ClientInvoiceForm(forms.Form):
    
    regular_hourly_rate = forms.DecimalField(required=False) 
    weekend_hourly_rate = forms.DecimalField(required=False) 
    holiday_hourly_rate = forms.DecimalField(required=False) 
    weekend_holiday_rate =forms.DecimalField(required=False) 
    live_in_rate =forms.DecimalField(required=False) 
    weekend_live_in_rate = forms.DecimalField(required=False) 
    holiday_live_in_rate =forms.DecimalField(required=False) 
    weekend_holiday_live_in_rate = forms.DecimalField(required=False) 
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(ClientInvoiceForm, self).clean()
        return cleaned_data

class FindClientTaskForm(forms.Form):

    client_email = forms.CharField(max_length=100)
    date_value = forms.DateField()
    
    def clean(self):
        cleaned_data = super(FindClientTaskForm, self).clean()
        return cleaned_data


