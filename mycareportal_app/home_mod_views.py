from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from mycareportal_app.models import *
from mycareportal_app.home_mod_forms import *
from django.views.generic import View

from django.contrib import messages

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from mycareportal_app.common import error_messaging as error_messaging
from django.contrib.sites.shortcuts import get_current_site
from mycareportal_app.email.home_mod_manager.home_mod_email_processor import HomeModEmailProcessor

from django.db import transaction

from django.shortcuts import redirect

import json

from django.core.urlresolvers import reverse

def contractor_dashboard(request):
    return render(request, 'production/contractor_dashboard.html')

def view_projects(request):
    return render(request, 'production/update_projects.html')

def view_bids(request):
    return render(request, 'production/view_bids.html')

class AddHomeModManager(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        context['home_mod_manager_form'] = HomeModManagerRegistrationForm()
        return render(request,'production/add_home_mod_manager.html', context)

    @transaction.atomic
    def post(self, request):
        context = {}
        add_home_mod_manager_form = HomeModManagerRegistrationForm(request.POST,request.FILES)
        context['home_mod_manager_form'] = add_home_mod_manager_form
        if add_home_mod_manager_form.is_valid():
            first_name = add_home_mod_manager_form.cleaned_data['first_name']
            last_name = add_home_mod_manager_form.cleaned_data['last_name']
            middle_name = add_home_mod_manager_form.cleaned_data['middle_name']
            gender = add_home_mod_manager_form.cleaned_data['gender']
            address = add_home_mod_manager_form.cleaned_data['address']
            city = add_home_mod_manager_form.cleaned_data['city']
            state = add_home_mod_manager_form.cleaned_data['state']
            zip_code = add_home_mod_manager_form.cleaned_data['zip_code']
            date_of_birth = add_home_mod_manager_form.cleaned_data['date_of_birth']
            phone_number = add_home_mod_manager_form.cleaned_data['phone_number']
            email = add_home_mod_manager_form.cleaned_data['email']
            profile_picture = add_home_mod_manager_form.cleaned_data['profile_picture']
            company = request.user.company
            #Create home mod user auth model and save
            try:
                with transaction.atomic():
                    new_user = User.objects.create_user(username=email,
                                                        email=email,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        company=company)
                    new_user.is_active = False
                    new_user.set_unusable_password()
                    new_user.save()
                    #Create home mod manager object and save
                    new_home_mod_manager = HomeModificationUser(user = new_user,
                                              first_name = first_name,
                                              last_name = last_name,
                                              middle_name = middle_name,
                                              gender = gender,
                                              address = address,
                                              city = city,
                                              state = state,
                                              zip_code = zip_code,
                                              date_of_birth = date_of_birth,
                                              phone_number = phone_number,
                                              email_address = email,
                                              company=company)
                    new_home_mod_manager.save()
                    #Save Image
                    new_home_mod_manager.profile_picture = profile_picture
                    new_home_mod_manager.save()
                    #Add new user to UserRoles with CAREGIVER Role
                    new_role = UserRoles(company=company,
                                            user=new_user,
                                            role='HOMEMODUSER')
                    new_role.save()
                    #Send verification email
                    current_site = get_current_site(request)
                    email_manager = HomeModEmailProcessor()
                    email_manager.send_verification_email(
                    new_user, current_site.domain
                    )
                    #Add messages
                    messages.success(request, "Home Modification Manager {0} {1} successfully added!".format(first_name, last_name))
                    return redirect('add_home_mod_manager')
            except IntegrityError as e:
                messages.error(request, "Home Modification user has already been registered. Please enter with a new email address.")
        else:
            form_errors = add_caregiver_form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
        return render(request, 'production/add_home_mod_manager.html', context)

class EditChooseHomeModUser(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_home_mod_users = HomeModificationUser.objects.filter(company=current_company).order_by('last_name')
        context['all_home_mod_users'] = all_home_mod_users
        context['find_home_mod_user_form'] = FindHomeModUserForm()
        return render(request, 'production/choose_edit_home_mod_user.html', context)

    def post(self, request):
        #Not really necessary - doesn't do anything right now
        context = {}
        return render(request, 'production/choose_edit_home_mod_user.html', context)

class EditHomeModUser(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        find_home_mod_user_form = FindHomeModUserForm(request.GET)
        current_company = request.user.company
        if find_home_mod_user_form.is_valid():
            home_mod_user_email = find_home_mod_user_form.cleaned_data['home_mod_user_email']
            home_mod_user = HomeModificationUser.objects.get(company=current_company,email_address=home_mod_user_email)
            home_mod_user_birthday = self.parse_date(home_mod_user.date_of_birth)
            edit_home_mod_user_form = HomeModUserEditForm(initial=
            {
                'first_name': home_mod_user.first_name,
                'last_name': home_mod_user.last_name,
                'middle_name': home_mod_user.middle_name,
                'gender': home_mod_user.gender,
                'address': home_mod_user.address,
                'city': home_mod_user.city,
                'state': home_mod_user.state,
                'zip_code': home_mod_user.zip_code,
                'date_of_birth': home_mod_user_birthday,
                'phone_number': home_mod_user.phone_number,
                'email': home_mod_user.email_address,
                'profile_picture': home_mod_user.profile_picture,
            })
            context['edit_home_mod_user_form'] = edit_home_mod_user_form
        else:
            form_errors = find_home_mod_user_form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
        return render(request, 'production/edit_home_mod_user.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_home_mod_user_form = HomeModUserEditForm(request.POST,request.FILES)
        email = request.POST.get('email')
        context['edit_home_mod_user_form'] = edit_home_mod_user_form
        if edit_home_mod_user_form.is_valid():
            try:
                first_name = edit_home_mod_user_form.cleaned_data['first_name']
                last_name = edit_home_mod_user_form.cleaned_data['last_name']
                middle_name = edit_home_mod_user_form.cleaned_data['middle_name']
                gender = edit_home_mod_user_form.cleaned_data['gender']
                address = edit_home_mod_user_form.cleaned_data['address']
                city = edit_home_mod_user_form.cleaned_data['city']
                state = edit_home_mod_user_form.cleaned_data['state']
                zip_code = edit_home_mod_user_form.cleaned_data['zip_code']
                date_of_birth = edit_home_mod_user_form.cleaned_data['date_of_birth']
                phone_number = edit_home_mod_user_form.cleaned_data['phone_number']
                email = edit_home_mod_user_form.cleaned_data['email']
                profile_picture = edit_home_mod_user_form.cleaned_data['profile_picture']
                #Get current caregiver
                home_mod_user = HomeModificationUser.objects.get(company=current_company,email_address=email)
                home_mod_user.first_name = first_name
                home_mod_user.last_name = last_name
                home_mod_user.middle_name = middle_name
                home_mod_user.gender = gender
                home_mod_user.address = address
                home_mod_user.city = city
                home_mod_user.state = state
                home_mod_user.zip_code = zip_code
                home_mod_user.date_of_birth = date_of_birth
                home_mod_user.phone_number = phone_number
                if profile_picture != None and home_mod_user.profile_picture != profile_picture:
                    home_mod_user.profile_picture = profile_picture
                if home_mod_user.email_address != None and home_mod_user.email_address != email:
                    home_mod_user.email_address = email
                    home_mod_user_auth = User.objects.get(company=current_company,email=email)
                    home_mod_user_auth.email = email
                    home_mod_user_auth.save()
                home_mod_user.save()
                print("SAVED HMU")
                messages.success(request, "Home Modification Manager {0} {1} successfully edited!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Home Modification Manager already exists. Please add a new Home Modification Manager")
        return HttpResponseRedirect(reverse('edit_home_mod_user') + "?home_mod_user_email=" + email)

    def parse_date(self,caregiver_birthday):
        caregiver_birthday = caregiver_birthday.date()
        output_month = caregiver_birthday.month
        output_day = caregiver_birthday.day
        output_year = caregiver_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

class Dashboard(LoginRequiredMixin, View):

    def get(self, request):

        context = {}
        return render(request, 'production/update_projects.html', context)

@login_required
def get_home_mod_with_email(request):
    if request.method == 'GET':
        context = {}
        email = request.GET.get('email_data')
        current_company = request.user.company
        home_mod_user = HomeModificationUser.objects.get(company=current_company,email_address = email)
        name = '{0} {1}'.format(home_mod_user.first_name, home_mod_user.last_name)
        address = '{0}, {1} {2} {3}'.format(home_mod_user.address, home_mod_user.city, home_mod_user.state, home_mod_user.zip_code)
        phone_number = home_mod_user.phone_number
        raw_dob = home_mod_user.date_of_birth
        date_of_birth = '{0}/{1}/{2}'.format(raw_dob.month,raw_dob.day,raw_dob.year)
        gender = home_mod_user.gender
        home_mod_user_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'date_of_birth': date_of_birth,
                        'gender': gender,
                        'email_address': email}
        if home_mod_user.profile_picture:
            home_mod_user_data['profile_picture'] = home_mod_user.profile_picture.url
        context["home_mod_user_data"] = home_mod_user_data
        #return JsonResponse(caregiver_data)
        return HttpResponse(json.dumps(home_mod_user_data), content_type="application/json")
