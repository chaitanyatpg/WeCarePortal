from django import forms
from mycareportal_app.models import *
from django.utils.translation import ugettext as _

class MoveManagerRegistrationForm(forms.Form):

    MIN_LENGTH = 8
    MAX_UPLOAD_SIZE = 5242880

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    middle_name = forms.CharField(max_length=100, required=False)
    gender = forms.CharField(max_length=1)
    address = forms.CharField(max_length=400)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
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

        cleaned_data = super(MoveManagerRegistrationForm, self).clean()
        self.clean_picture()
        return cleaned_data

class MoveManagerEditForm(forms.Form):

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

        cleaned_data = super(MoveManagerEditForm, self).clean()
        self.clean_picture()
        return cleaned_data

class FindMoveManagerForm(forms.Form):

    move_manager_email = forms.CharField(max_length=100)

    def clean(self):

        cleaned_data = super(FindMoveManagerForm, self).clean()
        return cleaned_data

class CreateMoveTaskForm(forms.Form):

    type_house = "HOUSE"
    type_townhouse = "TOWNHOUSE"
    type_apartment = "APARTMENT"
    type_senior_facility = "SENIORFACILITY"

    HOME_TYPE_CHOICES = (
    (type_house, "House"),
    (type_townhouse, "Townhouse"),
    (type_apartment, "Apartment"),
    (type_senior_facility, "Senior Facility")
    )

    type_city = "CITY"
    type_urban = "URBAN"
    type_suburban = "SUBURBAN"
    type_rural = "RURAL"

    AREA_TYPE_CHOICES = (
    (type_city, "City"),
    (type_urban, "Urban"),
    (type_suburban, "Suburban"),
    (type_rural, "Rural")
    )

    client_uid = forms.UUIDField(required=True)
    new_address_max_distance = forms.IntegerField(required=True)
    type_of_home = forms.ChoiceField(HOME_TYPE_CHOICES,required=True)
    provides_assistance = forms.BooleanField(required=True)
    minimum_cost = forms.IntegerField(required=True)
    maximum_cost = forms.IntegerField(required=True)
    type_of_area = forms.ChoiceField(AREA_TYPE_CHOICES,required=True)
    handicap_friendly = forms.BooleanField(required=True)
    furnished = forms.BooleanField(required=True)

class AddMoveInventoryForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    move_task_uid = forms.UUIDField(required=True)
    item = forms.CharField(max_length=50,required=True)
    item_quantity = forms.IntegerField()
    item_price = forms.IntegerField(required=False)
    #item_sales_price = forms.IntegerField(required=False)
    item_destination = forms.CharField(max_length=20, required=False)
    item_image = forms.ImageField(label='Select file', required=False)

    def clean_picture(self):
        picture = self.cleaned_data['item_image']
        if picture:
            if picture._size > self.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')

    def clean(self):

        cleaned_data = super(AddMoveInventoryForm, self).clean()
        self.clean_picture()
        return cleaned_data

class EditMoveInventoryForm(forms.Form):

    MAX_UPLOAD_SIZE = 5242880

    inventory_uid = forms.UUIDField(required=True)
    item = forms.CharField(max_length=50,required=True)
    item_quantity = forms.IntegerField()
    item_price = forms.IntegerField(required=False)
    item_sale_price = forms.IntegerField(required=False)
    item_destination = forms.CharField(max_length=20, required=False)
    item_sold = forms.BooleanField(required=False)
    item_image = forms.ImageField(label='Select file', required=False)

    def clean_picture(self):
        picture = self.cleaned_data['item_image']
        if picture:
            if picture._size > self.MAX_UPLOAD_SIZE:
                raise forms.ValidationError('Image is too large. Please upload an image that is less than 5mb')

    def clean(self):

        cleaned_data = super(EditMoveInventoryForm, self).clean()
        self.clean_picture()
        return cleaned_data

class BidForm(forms.Form):

    #contractor_uid = forms.UUIDField(required=true)
    task_uid = forms.UUIDField(required=True)
    start_date = forms.DateField(required=True)
    end_date = forms.DateField(required=True)
    cost = forms.IntegerField(required=True)
