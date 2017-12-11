from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
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
import csv
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

    @transaction.atomic
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
                                              company=company)
                    new_caregiver.save()
                    #Save Image
                    new_caregiver.profile_picture = profile_picture
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

class ChooseViewCaregiverTimesheet(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_caregivers = Caregiver.objects.filter(company=current_company).order_by('last_name')
        context['all_caregivers'] = all_caregivers
        context['find_caregiver_form'] = FindCaregiverForm()
        return render(request, 'production/choose_view_caregiver_timesheet.html', context)

class ViewCaregiverTimesheet(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        find_caregiver_form = FindCaregiverForm(request.GET)
        current_company = request.user.company
        if find_caregiver_form.is_valid():
            caregiver_email = find_caregiver_form.cleaned_data['caregiver_email']
            caregiver = Caregiver.objects.get(company=current_company,email_address=caregiver_email)
            caregiver_time_sheets = CaregiverTimeSheet.objects.filter(company=current_company, caregiver=caregiver, is_active=False)
            context['caregiver_time_sheets'] = self.construct_timesheet_rows(caregiver_time_sheets)
            return render(request, 'production/view_caregiver_timesheet.html', context)

    def construct_timesheet_rows(self, caregiver_time_sheets):
        caregiver_time_sheets = list(map(lambda x: {
                                                        "caregiver_name": "{0} {1}".format(x.caregiver.first_name,x.caregiver.last_name),
                                                        "client_name": "{0} {1}".format(x.client.first_name,x.client.last_name),
                                                        "clock_in_time": (x.clock_in_timestamp.astimezone(pytz.timezone(x.client_timezone))).replace(tzinfo=None),
                                                        "clock_out_time": (x.clock_out_timestamp.astimezone(pytz.timezone(x.client_timezone))).replace(tzinfo=None),
                                                        "time_worked": str(x.time_worked).split(".")[0]
                                                    }, caregiver_time_sheets))
        return caregiver_time_sheets

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
                'profile_picture': caregiver.profile_picture,
                'rating': caregiver.rating
            })
            print(caregiver.rating)
            context['edit_caregiver_form'] = edit_caregiver_form
            #Client Criteria map
            client_match_categories = ClientMatchCategory.objects.all()
            client_match_criteria = ClientMatchCriteria.objects.filter(is_default=True) | ClientMatchCriteria.objects.filter(company=current_company)

            caregiver_criteria_map = CaregiverCriteriaMap.objects.filter(company=current_company,caregiver=caregiver)
            caregiver_certification_map = CaregiverCertificationMap.objects.filter(company=current_company,caregiver=caregiver)
            caregiver_transfer_map = CaregiverTransferMap.objects.filter(company=current_company,caregiver=caregiver)

            criteria_map = self.make_criteria_map(client_match_categories,client_match_criteria,caregiver_criteria_map,current_company,caregiver)
            certification_map = self.make_certification_map(client_match_categories,client_match_criteria,caregiver_certification_map,current_company,caregiver)
            transfer_map = self.make_transfer_map(client_match_categories,client_match_criteria,caregiver_transfer_map,current_company,caregiver)

            context['criteria_map'] = criteria_map
            context['certification_map'] = certification_map
            context['transfer_map'] = transfer_map
        return render(request,'production/edit_caregiver.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_caregiver_form = CaregiverEditForm(request.POST,request.FILES)
        email = request.POST.get('email')
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
                rating = edit_caregiver_form.cleaned_data['rating']
                print ("RATING: " + str(rating))
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
                if self.arg_diff(caregiver.date_of_birth, date_of_birth):
                    caregiver.date_of_birth = date_of_birth
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
                caregiver.rating = rating
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

    def make_criteria_map(self, client_match_categories,client_match_criteria,caregiver_criteria_map,company,caregiver):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['General', 'Pets']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = caregiver_criteria_map.get_or_create(company=company,caregiver=caregiver,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

    def make_certification_map(self, client_match_categories,client_match_criteria,caregiver_certification_map,company,caregiver):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['Certifications']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = caregiver_certification_map.get_or_create(company=company,caregiver=caregiver,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

    def make_transfer_map(self, client_match_categories,client_match_criteria,caregiver_transfer_map,company,caregiver):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['Transfers']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = caregiver_transfer_map.get_or_create(company=company,caregiver=caregiver,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

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

@login_required
def caregiver_post_criteria(request):

    if request.method == "POST":
        company = request.user.company;
        status_id = request.POST['status_id']
        status_id = status_id.split('_')[0]
        status = request.POST['status']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        criteria_map = CaregiverCriteriaMap.objects.get(company=company,id=status_id)
        criteria_map.status = status
        criteria_map.save()
    return HttpResponse("Changed Status")

@login_required
def caregiver_post_certification(request):

    if request.method == "POST":
        company = request.user.company;
        status_id = request.POST['status_id']
        status_id = status_id.split('_')[0]
        status = request.POST['status']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        certification_map = CaregiverCertificationMap.objects.get(company=company,id=status_id)
        certification_map.status = status
        certification_map.save()
    return HttpResponse("Changed Status")

@login_required
def caregiver_post_transfer(request):

    if request.method == "POST":
        company = request.user.company;
        experience_id = request.POST['experience_id']
        experience_id = experience_id.split('_')[0]
        experience = request.POST['experience']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        transfer_map = CaregiverTransferMap.objects.get(company=company,id=experience_id)
        transfer_map.experience = experience
        transfer_map.save()
    return HttpResponse("Changed Status")

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
        #if caregiver.profile_picture:
        #    caregiver_data['profile_picture'] = caregiver.profile_picture.url
        #Get Tasks for assigned clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        tasks_not_complete = False #Bool for whether all tasks are complete (or cancelled)
        for client_data in assigned_clients:
            current_client_tasks = self.get_client_tasks(client_data, request)
            #if "tablet_id" in request.session:
            if not tasks_not_complete and current_client_tasks != None:
                tasks_not_complete = self.check_task_complete_status(current_client_tasks)
            if current_client_tasks != None:
                #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
                client_tasks[client_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        context["tasks_not_complete"] = tasks_not_complete
        #Get clock in and clock out information
        if "current_time_sheet" in request.session:
            current_time_sheet = CaregiverTimeSheet.objects.get(company=request.user.company, id=request.session['current_time_sheet'])
            time_sheet_clock_in = current_time_sheet.clock_in_timestamp
            current_time = timezone.now()
            clocked_in_time = current_time - time_sheet_clock_in
            context["clocked_in_time"] = str(clocked_in_time).split('.')[0]
        #Get Update Form
        context["update_task_form"] = UpdateTaskForm()
        #Get current date
        context["current_date"] = timezone.now()
        #Get default incidents
        default_incidents = DefaultIncidents.objects.all().order_by('incident')
        context['default_incidents'] = default_incidents
        #Get incident locations
        incident_locations = IncidentLocations.objects.all().order_by('location')
        context['incident_locations'] = incident_locations
        return render(request, 'production/caregiver_dashboard.html', context)

    @transaction.atomic
    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST, request.FILES)
        if update_task_form.is_valid():
            current_company = request.user.company
            comment = update_task_form.cleaned_data["comment"]
            task_id = update_task_form.cleaned_data["task_id"]
            client_id = update_task_form.cleaned_data["client_id"]
            client = Client.objects.get(company=current_company,id=client_id)
            status = update_task_form.cleaned_data["status"]
            incident_id = update_task_form.cleaned_data["incident_id"]
            location_id = update_task_form.cleaned_data["location_id"]
            attachments = request.FILES.getlist('attachment')
            task = TaskSchedule.objects.get(company=current_company,client=client,id=task_id)
            #task.comment = comment
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
            self.save_task_comments(request, update_task_form, task, current_company, client, comment)
            self.save_task_attachments(request, update_task_form, task, current_company, client, request.user, attachments)
            if(incident_id and location_id):
                self.report_incident(request, update_task_form, incident_id, location_id, client, request.user, task)
            messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return redirect('caregiver_dashboard')

    def report_incident(self, request, update_task_form, incident_id, location_id, client, user, task):

        incident = DefaultIncidents.objects.get(id = incident_id)
        location = IncidentLocations.objects.get(id = location_id)
        incident_report = IncidentReport(company = request.user.company,
                                        client = client,
                                        reporter = user,
                                        task=task,
                                        incident = incident,
                                        location = location,
                                        incident_name = incident.incident,
                                        location_name = location.location
                                        )
        incident_report.save()
        messages.success(request, "Reported Incident: {0} at location {1}".format(incident.incident, location.location))

    def save_task_attachments(self, request, update_task_form, task, current_company, client, user, attachments):
        for uploaded_file in attachments:
            task_attachment = TaskAttachment(company=current_company,
                                            client=client,
                                            user=user,
                                            task_schedule=task,
                                            attachment=uploaded_file)
            task_attachment.save()

    def save_task_comments(self, request, update_task_form, task, current_company, client, comment):

        #caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        task_comment = TaskComment(company=current_company,
                                    client=client,
                                    user=request.user,
                                    task_schedule=task,
                                    comment=comment)
        if comment != "":
            task_comment.save()

    def get_client_tasks(self, client_data, request):
        client_timezone = pytz.timezone(client_data.time_zone)
        #current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        timezone.activate(client_timezone)
        if "tablet_id" in request.session:
            tablet_id = request.session["tablet_id"]
            tablet_client = ClientTabletRegister.objects.get(company=request.user.company,device_id=tablet_id)
            if tablet_client.client == client_data:
                client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date).order_by('complete','cancelled','pending','in_progress')
                client_tasks = list(map(lambda x: (x,
                TaskComment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
                TaskAttachment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
                TaskLink.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created')),client_tasks))
                return client_tasks
            else:
                return None
        else:
            client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date).order_by('complete','cancelled','pending','in_progress')
            client_tasks = list(map(lambda x: (x,
            TaskComment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
            TaskAttachment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
            TaskLink.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created')),client_tasks))
            return client_tasks

    def check_task_complete_status(self, current_client_tasks):
        for task in current_client_tasks:
            if not(task[0].complete or task[0].cancelled):
                return True
        return False

class SelectShiftsChoose(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        context['all_caregivers'] = Caregiver.objects.filter(company=company).order_by('last_name')
        context['find_caregiver_form'] = FindCaregiverForm()
        return render(request, 'production/schedule_shifts_choose.html', context)

class ScheduleShifts(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        find_caregiver_form = FindCaregiverForm(request.GET)
        if find_caregiver_form.is_valid():
            caregiver_email = find_caregiver_form.cleaned_data['caregiver_email']
            caregiver = Caregiver.objects.get(company=current_company,email_address=caregiver_email)
            clients = Client.objects.filter(company=current_company)
            assigned_clients = []
            for client in clients:
                if caregiver in client.caregiver.all():
                    assigned_clients.append(client)
            context['caregiver'] = caregiver
            context['assigned_clients'] = assigned_clients
            context['schedule_shift_form'] = ScheduleShiftForm()
            context['delete_schedule_form'] = DeleteScheduleForm()
            context['edit_schedule_form'] = EditScheduleForm()
            context['caregiver_shifts'] = CaregiverSchedule.objects.filter(company=current_company,caregiver=caregiver)
            print(context['caregiver_shifts'])
            return render(request, 'production/schedule_shifts.html', context)
        else:
            messages.success(request, "There was an error processing the previous request. Please contact a system administrator")
            return redirect('select_shifts_choose')

    def post(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        schedule_shifts_form = ScheduleShiftForm(request.POST)
        if schedule_shifts_form.is_valid():
            caregiver_id = schedule_shifts_form.cleaned_data['caregiver_id']
            client_id = schedule_shifts_form.cleaned_data['client_id']
            start_date = schedule_shifts_form.cleaned_data['start_date']
            end_date = schedule_shifts_form.cleaned_data['end_date']
            start_hour = schedule_shifts_form.cleaned_data['start_hour']
            start_minute = schedule_shifts_form.cleaned_data['start_minute']
            end_hour = schedule_shifts_form.cleaned_data['end_hour']
            end_minute = schedule_shifts_form.cleaned_data['end_minute']
            assigned_caregiver = Caregiver.objects.get(company=current_company, id=caregiver_id)
            assigned_client = Client.objects.get(company=current_company, id=client_id)
            start_time = ""
            end_time = ""
            if start_hour != "" and start_minute != "":
                start_time = "{0}:{1}".format(str(start_hour),str(start_minute))
                start_time = datetime.datetime.strptime(start_time,'%H:%M').time()
            if end_hour != "" and end_minute != "":
                end_time = "{0}:{1}".format(str(end_hour),str(end_minute))
                end_time = datetime.datetime.strptime(end_time,'%H:%M').time()
            date_range_num = end_date - start_date
            caregiver_schedule_header = CaregiverScheduleHeader(company=current_company,
                                                    caregiver = assigned_caregiver,
                                                    client = assigned_client,
                                                    start_date = start_date,
                                                    end_date = end_date,
                                                    start_time = start_time,
                                                    end_time = end_time)
            caregiver_schedule_header.save()
            for i in range(date_range_num.days + 1):
                new_date = (start_date + datetime.timedelta(days=i))
                print(start_time)
                print(end_time)
                print(new_date)
                caregiver_schedule = CaregiverSchedule(company=current_company,
                                                        caregiver = assigned_caregiver,
                                                        client = assigned_client,
                                                        date = new_date,
                                                        start_time = start_time,
                                                        end_time = end_time,
                                                        schedule_header=caregiver_schedule_header)
                caregiver_schedule.save()
        return HttpResponseRedirect(reverse('schedule_shifts') + "?caregiver_email=" + assigned_caregiver.email_address)

@login_required
def get_schedule_with_id(request):
    company = request.user.company
    caregiver_id = request.GET.get('caregiver_id')
    schedule_id = request.GET.get('schedule_id')
    schedule_entry = CaregiverSchedule.objects.get(company=company,
                                                caregiver__id = caregiver_id,
                                                id=schedule_id)
    client = schedule_entry.client
    start_hour = str(schedule_entry.start_time.hour).zfill(2)
    start_minute = str(schedule_entry.end_time.minute).zfill(2)
    end_hour = str(schedule_entry.end_time.hour).zfill(2)
    end_minute = str(schedule_entry.end_time.minute).zfill(2)
    schedule_data = {
        "schedule_id": schedule_id,
        "client_id": client.id,
        "client_name": "{0} {1}".format(client.first_name,client.last_name),
        "start_hour": start_hour,
        "start_minute": start_minute,
        "end_hour": end_hour,
        "end_minute": end_minute
    }
    return HttpResponse(json.dumps(schedule_data), content_type="application/json")

@login_required
def edit_schedule_with_id(request):
    company = request.user.company
    edit_schedule_form = EditScheduleForm(request.POST, request.FILES)
    caregiver_id = request.POST.get('caregiver_id')
    if edit_schedule_form.is_valid():
        caregiver_id = edit_schedule_form.cleaned_data['caregiver_id']
        schedule_id = edit_schedule_form.cleaned_data['schedule_id']
        start_hour = edit_schedule_form.cleaned_data['start_hour']
        end_hour = edit_schedule_form.cleaned_data['end_hour']
        start_minute = edit_schedule_form.cleaned_data['start_minute']
        end_minute = edit_schedule_form.cleaned_data['end_minute']
        start_time = None
        end_time= None
        if start_hour != "" and start_minute != "":
            start_time = "{0}:{1}".format(str(start_hour),str(start_minute))
            start_time = datetime.datetime.strptime(start_time,'%H:%M').time()
        if end_hour != "" and end_minute != "":
            end_time = "{0}:{1}".format(str(end_hour),str(end_minute))
            end_time = datetime.datetime.strptime(end_time,'%H:%M').time()
        schedule_entry = CaregiverSchedule.objects.get(company=company,
                                                    caregiver__id=caregiver_id,
                                                    id=schedule_id)
        if start_time:
            schedule_entry.start_time = start_time
        if end_time:
            schedule_entry.end_time = end_time
        schedule_entry.save()
    current_caregiver = Caregiver.objects.get(company=company, id=caregiver_id)
    caregiver_email = current_caregiver.email_address
    return HttpResponseRedirect(reverse('schedule_shifts') + "?caregiver_email=" + caregiver_email)

@login_required
def delete_schedule_with_id(request):
    company = request.user.company
    caregiver_id = request.POST.get('caregiver_id')
    schedule_id = request.POST.get('schedule_id')
    schedule_entry = CaregiverSchedule.objects.get(company=company,
                                                caregiver__id = caregiver_id,
                                                id=schedule_id)
    schedule_entry.delete()
    return HttpResponse("Delete Successful")

@login_required
def delete_recurring_schedule_with_id(request):
    if request.method == 'POST':
        context = {}
        company=request.user.company
        caregiver_id = request.POST.get('caregiver_id')
        schedule_id = request.POST.get('schedule_id')
        schedule_entry = CaregiverSchedule.objects.get(company=company,
                                                    caregiver__id = caregiver_id,
                                                    id=schedule_id)
        schedule_header = schedule_entry.schedule_header
        all_recurring_schedule_ids = []
        if schedule_header != None:
            all_recurring_schedule_entries = CaregiverSchedule.objects.filter(company=company,
                                                                            caregiver_id = caregiver_id,
                                                                            schedule_header=schedule_header)
            all_recurring_schedule_ids = list(map(lambda x: x.id, all_recurring_schedule_entries))
            for recurring_schedule_entry in all_recurring_schedule_entries:
                recurring_schedule_entry.delete()
        return HttpResponse(json.dumps(all_recurring_schedule_ids),content_type="application/json")

@login_required
def get_assigned_clients_with_caregiver_with_id(request):
    company = request.user.company
    caregiver_email = request.GET.get('email_data')
    caregiver = Caregiver.objects.get(company=company, email_address=caregiver_email)
    clients = Client.objects.filter(company=company)
    assigned_clients = []
    for client in clients:
        if caregiver in client.caregiver.all():
            assigned_clients.append(client)
    assigned_clients = serializers.serialize('json',assigned_clients)
    return HttpResponse(json.dumps(assigned_clients), content_type="application/json")

@login_required
def caregiver_dashboard(request):
    return render(request, 'production/caregiver_dashboard.html')

@login_required
def calendar(request):
    return render(request, 'production/task_calendar.html')

@login_required
def export_all_caregiver_timesheets(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_caregiver_timesheets.csv"'

    writer = csv.writer(response)
    writer.writerow(['Caregiver', 'Client', 'Clock in Timestamp', 'Clock out Timestamp', 'Client Timezone', 'Time Worked'])

    caregiver_timesheets = CaregiverTimeSheet.objects.filter(company=request.user.company)
    for timesheet in caregiver_timesheets:
        parsed_timesheet = ["{0} {1}".format(timesheet.caregiver.first_name,timesheet.caregiver.last_name),
                            "{0} {1}".format(timesheet.client.first_name,timesheet.client.last_name),
                            str(timesheet.clock_in_timestamp.astimezone(pytz.timezone(timesheet.client_timezone)).replace(tzinfo=None)).split(".")[0],
                            str(timesheet.clock_out_timestamp.astimezone(pytz.timezone(timesheet.client_timezone)).replace(tzinfo=None)).split(".")[0],
                            timesheet.client_timezone,
                            str(timesheet.time_worked).split(".")[0]]
        writer.writerow(parsed_timesheet)
    return response
