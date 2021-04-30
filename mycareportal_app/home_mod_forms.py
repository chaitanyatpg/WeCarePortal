from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class HomeModManagerRegistrationForm(forms.Form):

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
    email = forms.CharField(max_length=200)
    profile_picture = forms.ImageField(label='Select file', required=False)

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

        cleaned_data = super(HomeModManagerRegistrationForm, self).clean()
        self.clean_picture()
        return cleaned_data

class HomeModUserEditForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1, required=False)
    address = forms.CharField(max_length=400, required=False)
    city = forms.CharField(max_length=100, required=False)
    state = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    date_of_birth = forms.DateTimeField(required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=200, required=False)
    profile_picture = forms.ImageField(label='Select file', required=False)

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

        cleaned_data = super(HomeModUserEditForm, self).clean()
        self.clean_picture()
        return cleaned_data

class FindHomeModUserForm(forms.Form):

    home_mod_user_email = forms.CharField(max_length=100)

    def clean(self):

        cleaned_data = super(FindHomeModUserForm, self).clean()
        return cleaned_data

class BidForm(forms.Form):

    #contractor_uid = forms.UUIDField(required=true)
    task_uid = forms.UUIDField(required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    cost = forms.IntegerField(required=True)



