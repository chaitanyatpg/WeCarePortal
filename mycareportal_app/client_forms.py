from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class ClientRegistrationForm(forms.Form):

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
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    time_zone = forms.CharField(max_length=50)
    profile_picture = forms.ImageField(label='Select file', required=False)
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('Image file type is not recognized. Please try again')
        return picture

    def clean(self):

        cleaned_data = super(ClientRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class EditClientDetailsForm(forms.Form):

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
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    time_zone = forms.CharField(max_length=50)
    profile_picture = forms.ImageField(label='Select file', required=False)
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('Image file type is not recognized. Please try again')
        return picture

    def clean(self):

        cleaned_data = super(EditClientDetailsForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class FamilyDetailsForm(forms.Form):

    client_email = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    relationship = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    email = forms.CharField(max_length=200)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    power_of_attorney = forms.BooleanField(required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)
    password = forms.CharField(max_length=30, required=False)
    confirm_password = forms.CharField(max_length=30, required=False)
    family_id = forms.IntegerField(required=False)

    def clean_picture(self):
        picture = self.cleaned_data['profile_picture']
        if not picture:
            return None
        if not picture.content_type or not picture.content_type.startswith('image'):
            raise forms.ValidationError('Image file type is not recognized. Please try again')
        return picture

    def clean(self):
        cleaned_data = super(FamilyDetailsForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class DeleteFamilyDetailsForm(forms.Form):

    family_id = forms.IntegerField()
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(DeleteFamilyDetailsForm, self).clean()
        return cleaned_data

class ProviderDetailsForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    #provider_type = forms.CharField(max_length=100)
    speciality = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=20)
    secondary_phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200)
    password = forms.CharField(max_length=30,required=False)
    confirm_password = forms.CharField(max_length=30,required=False)
    provider_id = forms.IntegerField(required=False)
    client_email = forms.CharField(max_length=200)

    def clean(self):
        cleaned_data = super(ProviderDetailsForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
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
    fax_number = forms.CharField(max_length=50)
    email = forms.CharField(max_length=200)
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
    fax_number = forms.CharField(max_length=50)
    email = forms.CharField(max_length=200)
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

    client_email = forms.CharField(max_length=200)
    task = forms.CharField(max_length=300)
    task_type = forms.CharField(max_length=100)
    start_date = forms.DateTimeField()
    end_date = forms.DateTimeField()
    start_hour = forms.CharField(required=False)
    start_minute = forms.CharField(required=False)
    end_hour = forms.CharField(required=False)
    end_minute = forms.CharField(required=False)
    description = forms.CharField(required=False, max_length=1000)
    link = forms.CharField(required=False, max_length=500)
    attachment = forms.FileField(label='Select file', required=False)

    def clean(self):
        cleaned_data = super(AssignTaskForm, self).clean()
        return cleaned_data

class FindClientForm(forms.Form):

    client_email = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super(FindClientForm, self).clean()
        return cleaned_data

class EditTaskForm(forms.Form):

    task_id = forms.IntegerField()
    start_time = forms.CharField(max_length=10, required=False)
    end_time = forms.CharField(max_length=10, required=False)
    description = forms.CharField(max_length=1000, required=False)
    link = forms.CharField(max_length=500, required=False)
    attachment = forms.FileField(label='Select file', required=False)

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
