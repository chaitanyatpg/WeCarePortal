from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db import transaction
from mycareportal_app.models import *
from mycareportal_app.caregiver_forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import View
import datetime
import pytz
import django.utils.timezone as timezone
import json
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

def add_caregiver(request):
    return render(request, 'production/add_caregiver.html')

class AddCaregiver(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        context['add_caregiver_form'] = CaregiverRegistrationForm()
        return render(request,'production/add_caregiver.html', context)

    def post(self, request):
        context = {}
        add_caregiver_form = CaregiverRegistrationForm(request.POST,request.FILES)
        context['add_caregiver_form'] = add_caregiver_form
        if add_caregiver_form.is_valid():
            first_name = add_caregiver_form.cleaned_data['first_name']
            last_name = add_caregiver_form.cleaned_data['last_name']
            middle_name = add_caregiver_form.cleaned_data['middle_name']
            gender = add_caregiver_form.cleaned_data['gender']
            address = add_caregiver_form.cleaned_data['address']
            city = add_caregiver_form.cleaned_data['city']
            state = add_caregiver_form.cleaned_data['state']
            zip_code = add_caregiver_form.cleaned_data['zip_code']
            date_of_birth = add_caregiver_form.cleaned_data['date_of_birth']
            phone_number = add_caregiver_form.cleaned_data['phone_number']
            secondary_phone_number = add_caregiver_form.cleaned_data['secondary_phone_number']
            email = add_caregiver_form.cleaned_data['email']
            password = add_caregiver_form.cleaned_data['password']
            ssn = add_caregiver_form.cleaned_data['ssn']
            referrer = add_caregiver_form.cleaned_data['referrer']
            profile_picture = add_caregiver_form.cleaned_data['profile_picture']
            company = request.user.company
            #Create caregiver user auth model and save
            try:
                with transaction.atomic():
                    new_user = User.objects.create_user(username=email,
                                                        email=email,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        password=password,
                                                        company=company)
                    new_user.save()
                    #Create caregiver object and save
                    new_caregiver = Caregiver(user = new_user,
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
                                              secondary_phone_number = secondary_phone_number,
                                              email_address = email,
                                              ssn = ssn,
                                              referrer = referrer,
                                              profile_picture = profile_picture,
                                              company=company)
                    new_caregiver.save()
                    #Add new user to UserRoles with CAREGIVER Role
                    new_role = UserRoles(company=company,
                                            user=new_user,
                                            role='CAREGIVER')
                    new_role.save()
                    #Add messages
                    messages.success(request, "Caregiver {0} {1} successfully added!".format(first_name, last_name))
                    return redirect('add_caregiver')
            except IntegrityError as e:
                messages.error(request, "Caregiver has already been registered. Please enter a new email address.")
        return render(request, 'production/add_caregiver.html', context)

class EditChooseCaregiver(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_caregivers = Caregiver.objects.filter(company=current_company).order_by('last_name')
        context['all_caregivers'] = all_caregivers
        context['find_caregiver_form'] = FindCaregiverForm()
        return render(request, 'production/choose_edit_caregiver.html', context)

    def post(self, request):
        #Not really necessary - doesn't do anything right now
        context = {}
        return render(request, 'production/choose_edit_caregiver.html', context)

class EditCaregiver(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        find_caregiver_form = FindCaregiverForm(request.GET)
        current_company = request.user.company
        if find_caregiver_form.is_valid():
            caregiver_email = find_caregiver_form.cleaned_data['caregiver_email']
            caregiver = Caregiver.objects.get(company=current_company,email_address=caregiver_email)
            caregiver_birthday = self.parse_date(caregiver.date_of_birth)
            edit_caregiver_form = CaregiverEditForm(initial=
            {
                'first_name': caregiver.first_name,
                'last_name': caregiver.last_name,
                'middle_name': caregiver.middle_name,
                'gender': caregiver.gender,
                'address': caregiver.address,
                'city': caregiver.city,
                'state': caregiver.state,
                'zip_code': caregiver.zip_code,
                'date_of_birth': caregiver_birthday,
                'phone_number': caregiver.phone_number,
                'secondary_phone_number': caregiver.secondary_phone_number,
                'email': caregiver.email_address,
                'ssn': caregiver.ssn,
                'referrer': caregiver.referrer,
                'profile_picture': caregiver.profile_picture
            })
            context['edit_caregiver_form'] = edit_caregiver_form
        return render(request,'production/edit_caregiver.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_caregiver_form = CaregiverEditForm(request.POST,request.FILES)
        context['edit_caregiver_form'] = edit_caregiver_form
        if edit_caregiver_form.is_valid():
            try:
                first_name = edit_caregiver_form.cleaned_data['first_name']
                last_name = edit_caregiver_form.cleaned_data['last_name']
                middle_name = edit_caregiver_form.cleaned_data['middle_name']
                gender = edit_caregiver_form.cleaned_data['gender']
                address = edit_caregiver_form.cleaned_data['address']
                city = edit_caregiver_form.cleaned_data['city']
                state = edit_caregiver_form.cleaned_data['state']
                zip_code = edit_caregiver_form.cleaned_data['zip_code']
                date_of_birth = edit_caregiver_form.cleaned_data['date_of_birth']
                phone_number = edit_caregiver_form.cleaned_data['phone_number']
                secondary_phone_number = edit_caregiver_form.cleaned_data['secondary_phone_number']
                email = edit_caregiver_form.cleaned_data['email']
                ssn = edit_caregiver_form.cleaned_data['ssn']
                referrer = edit_caregiver_form.cleaned_data['referrer']
                profile_picture = edit_caregiver_form.cleaned_data['profile_picture']
                #Get current caregiver
                caregiver = Caregiver.objects.get(company=current_company,email_address=email)
                if self.arg_diff(caregiver.first_name, first_name):
                    caregiver.first_name = first_name
                if self.arg_diff(caregiver.last_name, last_name):
                    caregiver.last_name = last_name
                if self.arg_diff(caregiver.middle_name, middle_name):
                    caregiver.middle_name = middle_name
                if self.arg_diff(caregiver.gender, gender):
                    caregiver.gender = gender
                if self.arg_diff(caregiver.address, address):
                    caregiver.address = address
                if self.arg_diff(caregiver.city, city):
                    caregiver.city = city
                if self.arg_diff(caregiver.state, state):
                    caregiver.state = state
                if self.arg_diff(caregiver.zip_code, zip_code):
                    caregiver.zip_code = zip_code
                #caregiver.date_of_birth = date_of_birth
                if self.arg_diff(caregiver.phone_number, phone_number):
                    caregiver.phone_number = phone_number
                if self.arg_diff(caregiver.secondary_phone_number, secondary_phone_number):
                    caregiver.secondary_phone_number = secondary_phone_number
                if self.arg_diff(caregiver.ssn, ssn):
                    caregiver.ssn = ssn
                if self.arg_diff(caregiver.referrer, referrer):
                    caregiver.referrer = referrer
                if self.arg_diff(caregiver.profile_picture, profile_picture):
                    caregiver.profile_picture = profile_picture
                if self.arg_diff(caregiver.email_address, email):
                    caregiver.email_address = email
                    caregiver_auth = User.objects.get(company=current_company,email=email)
                    caregiver_auth.email = email
                    caregiver_auth.save()
                caregiver.save()
                messages.success(request, "Caregiver {0} {1} successfully edited!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Caregiver already exists. Please add a new Caregiver")
        return HttpResponseRedirect(reverse('edit_caregiver') + "?caregiver_email=" + email)

    def arg_diff(self,old,new):
        return (new != None and old != new)

    def parse_date(self,caregiver_birthday):
        caregiver_birthday = caregiver_birthday.date()
        output_month = caregiver_birthday.month
        output_day = caregiver_birthday.day
        output_year = caregiver_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

@login_required
def get_caregiver_with_email(request):
    if request.method == 'GET':
        context = {}
        email = request.GET.get('email_data')
        current_company = request.user.company
        caregiver = Caregiver.objects.get(company=current_company,email_address = email)
        name = '{0} {1}'.format(caregiver.first_name, caregiver.last_name)
        address = '{0}, {1} {2} {3}'.format(caregiver.address, caregiver.city, caregiver.state, caregiver.zip_code)
        phone_number = caregiver.phone_number
        raw_dob = caregiver.date_of_birth
        date_of_birth = '{0}/{1}/{2}'.format(raw_dob.month,raw_dob.day,raw_dob.year)
        gender = caregiver.gender
        caregiver_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'date_of_birth': date_of_birth,
                        'gender': gender,
                        'email_address': email}
        if caregiver.profile_picture:
            caregiver_data['profile_picture'] = caregiver.profile_picture.url
        context["caregiver_data"] = caregiver_data
        #return JsonResponse(caregiver_data)
        return HttpResponse(json.dumps(caregiver_data), content_type="application/json")

class CaregiverDashboard(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        assigned_clients = Client.objects.filter(company=current_company,caregiver=caregiver)
        context["current_caregiver"] = caregiver
        #Get displayable caregiver data
        name = '{0} {1}'.format(caregiver.first_name, caregiver.last_name)
        address = '{0}, {1} {2} {3}'.format(caregiver.address, caregiver.city, caregiver.state, caregiver.zip_code)
        phone_number = caregiver.phone_number
        raw_dob = caregiver.date_of_birth
        date_of_birth = '{0}/{1}/{2}'.format(raw_dob.month,raw_dob.day,raw_dob.year)
        gender = caregiver.gender
        caregiver_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'date_of_birth': date_of_birth,
                        'gender': gender}
        context["caregiver_data"] = caregiver_data
        if caregiver.profile_picture:
            caregiver_data['profile_picture'] = caregiver.profile_picture.url
        #Get Tasks for assigned clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        for client_data in assigned_clients:
            current_client_tasks = self.get_client_tasks(client_data, request)
            if current_client_tasks != None:
                #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
                client_tasks[client_data] = list(current_client_tasks)
        #print(current_date)
        context["client_tasks"] = client_tasks
        #Get Update Form
        context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/caregiver_dashboard.html', context)

    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST)
        if update_task_form.is_valid():
            current_company = request.user.company
            comment = update_task_form.cleaned_data["comment"]
            task_id = update_task_form.cleaned_data["task_id"]
            client_id = update_task_form.cleaned_data["client_id"]
            status = update_task_form.cleaned_data["status"]
            task = TaskSchedule.objects.get(company=current_company,client=client_id,id=task_id)
            task.comment = comment
            if status == "pending":
                task.pending = True
                task.complete = False
                task.in_progress = False
                task.cancelled = False
            elif status == "complete":
                task.pending = False
                task.complete = True
                task.in_progress = False
                task.cancelled = False
            elif status == "in_progress":
                task.pending = False
                task.complete = False
                task.in_progress = True
                task.cancelled = False
            elif status == "cancelled":
                task.pending = False
                task.complete = False
                task.in_progress = False
                task.cancelled = True
            task.save()
            messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return redirect('caregiver_dashboard')

    def get_client_tasks(self, client_data, request):
        client_timezone = pytz.timezone(client_data.time_zone)
        #current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        if "tablet_id" in request.session:
            tablet_id = request.session["tablet_id"]
            tablet_client = ClientTabletRegister.objects.get(company=request.user.company,device_id=tablet_id)
            if tablet_client.client == client_data:
                client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date).order_by('complete','cancelled','pending','in_progress')
                return client_tasks
            else:
                return None
        else:
            client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date).order_by('complete','cancelled','pending','in_progress')
            return client_tasks

@login_required
def caregiver_dashboard(request):
    return render(request, 'production/caregiver_dashboard.html')

@login_required
def calendar(request):
    return render(request, 'production/task_calendar.html')
