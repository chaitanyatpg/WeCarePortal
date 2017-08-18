from django import forms
from django.contrib.auth.models import User
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class ManagerRegistrationForm(forms.Form):

    company_name = forms.CharField(max_length=200)
    email = forms.CharField(max_length=200)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)
    contact_number = forms.CharField(max_length=20)
    password = forms.CharField(max_length=30)
    confirm_password = forms.CharField(max_length=30)

    def clean(self):

        cleaned_data = super(ManagerRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class CareManagerRegistrationForm(forms.Form):

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.CharField(max_length=200)
    password = forms.CharField(max_length=30)
    confirm_password = forms.CharField(max_length=30)
    can_add = forms.BooleanField(required=False)

    def clean(self):

        cleaned_data = super(CareManagerRegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError(
                            _('Passwords do not match'),
                            code='invalid',
                            params={'value': 'Passwords do not match'})
        return cleaned_data

class CompanyEditForm(forms.Form):

    company_name = forms.CharField(max_length=200)
    contact_number = forms.CharField(max_length=20)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=2)
    zip_code = forms.CharField(max_length=10)

    def clean(self):

        cleaned_data = super(CompanyEditForm, self).clean()
        return cleaned_data
