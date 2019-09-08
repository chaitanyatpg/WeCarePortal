from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _
import re

class ManagerRegistrationForm(forms.Form):
    MIN_LENGTH = 8

    company_name = forms.CharField(max_length=200)
    email = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)
    contact_number = forms.CharField(max_length=20)
    password = forms.CharField(max_length=30)
    confirm_password = forms.CharField(max_length=30)
    time_zone = forms.CharField(max_length=50)
    activation_code = forms.CharField(max_length=22, required=False)

    def clean(self):

        cleaned_data = super(ManagerRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        if (not(bool(re.match("(?=.*[A-Z])",password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if (not(bool(re.search(r'\d',password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))

        return cleaned_data

class CareManagerRegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.CharField(max_length=200)
    can_add = forms.BooleanField(required=False)

    def clean(self):

        cleaned_data = super(CareManagerRegistrationForm, self).clean()
        return cleaned_data

class CompanyEditForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    company_name = forms.CharField(max_length=200)
    contact_number = forms.CharField(max_length=20)
    address = forms.CharField(max_length=400,required=False)
    city = forms.CharField(max_length=100,required=False)
    state = forms.CharField(max_length=100,required=False)
    zip_code = forms.CharField(max_length=10,required=False)
    account_number = forms.IntegerField(required=False)
    time_zone = forms.CharField(max_length=50, required=False)
    default_dashboard = forms.CharField(max_length=100, required=False)
    tax_rate = forms.DecimalField(required=False)
    logo = forms.ImageField(label='Select file', required=False)

    def clean_picture(self):
        picture = self.cleaned_data['logo']
        if picture:
            if picture._size > self.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')

    def clean(self):
        cleaned_data = super(CompanyEditForm, self).clean()
        self.clean_picture()
        return cleaned_data

class CloseCaregiverSessionForm(forms.Form):

    caregiver_session_id = forms.IntegerField()
    clock_out_date = forms.DateField(required=False)
    end_hour = forms.CharField(required=False)
    end_minute = forms.CharField(required=False)
    reason = forms.CharField(max_length=200,required=False)

    def clean(self):

        cleaned_data = super(CloseCaregiverSessionForm, self).clean()
        return cleaned_data

class PasswordResetForm(forms.Form):

    MIN_LENGTH = 8

    password = forms.CharField(max_length=30,required=True)
    confirm_password = forms.CharField(max_length=30,required=True)
    uidb64 = forms.CharField(required=True)
    token = forms.CharField(required=True)
    user_id = forms.IntegerField(required=True)

    def clean(self):

        cleaned_data = super(PasswordResetForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        if (not(bool(re.match("(?=.*[A-Z])",password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if (not(bool(re.search(r'\d',password)))):
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))
        if len(password) < self.MIN_LENGTH:
            raise forms.ValidationError("Password must be at least {0} characters long, have one capital letter and one number".
                                        format(self.MIN_LENGTH))

        return cleaned_data

class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(required=True)

    def clean(self):
        cleaned_data = super(ForgotPasswordForm, self).clean()
        return cleaned_data

class CreateHomeModTaskForm(forms.Form):

    client_uid = forms.UUIDField(required=True)
    assessment_category_uid = forms.UUIDField(required=True)
    task_name= forms.CharField(max_length = 100,required=True)
    task_description = forms.CharField(max_length = 500,required=True)

    def clean(self):

        cleaned_data = super(CreateHomeModTaskForm, self).clean()
        return cleaned_data

class ChooseClientInvoiceForm(forms.Form):

    client_email = forms.CharField(max_length=100)
    start_date = forms.DateField()
    end_date = forms.DateField()

    def clean(self):
        cleaned_data = super(ChooseClientInvoiceForm, self).clean()
        return cleaned_data
