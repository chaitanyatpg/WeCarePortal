from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import redirect
from mycareportal_app.models import *
from mycareportal_app.client_forms import *
from django.views.generic import View
from django.http import JsonResponse
from collections import defaultdict
from dateutil import relativedelta
import datetime
import json
import pytz
import django.utils.timezone as timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

@login_required
def add_client(request):
    return render(request, 'production/care_portal.html')

class ActivateTabletClient(LoginRequiredMixin, View):

    def get(self,request):
        context = {}
        current_company = request.user.company
        find_client_form = FindClientForm(request.GET,request.FILES)
        if find_client_form.is_valid():
            client_email = find_client_form.cleaned_data['client_email']
            client = Client.objects.get(company=current_company, email_address=client_email)
            #reg_status = ClientTabletRegister.objects.get(company=current_company, client=client)
            context["current_client"] = client
            context["register_client_tablet_form"] = RegisterClientTabletForm()
            return render(request,'production/activate_tablet_client.html',context)

    @transaction.atomic
    def post(self,request):
        context = {}
        current_company = request.user.company
        register_client_tablet_form = RegisterClientTabletForm(request.POST)
        if register_client_tablet_form.is_valid():
            client_id = register_client_tablet_form.cleaned_data['client_id']
            client = Client.objects.get(company=current_company,id=client_id)
            tablet_id = register_client_tablet_form.cleaned_data['tablet_id']
            client_tablet_register = ClientTabletRegister(company=current_company,
                                                            client=client,
                                                            device_id=tablet_id)
            #get row and delete with same client if exists
            if ClientTabletRegister.objects.filter(company=current_company,client=client).exists():
                existing_register = ClientTabletRegister.objects.get(company=current_company,client=client)
                existing_register.delete()
            #get row and delete with same tablet_id if exists
            if ClientTabletRegister.objects.filter(device_id=tablet_id).exists():
                existing_register = ClientTabletRegister.objects.get(device_id=tablet_id)
                existing_register.delete()
            client_tablet_register.save()
            messages.success(request, "Client {0} {1} successfully registered to tablet!".format(client.first_name,client.last_name))
        return redirect('activate_tablet_choose_client')

class ActivateTabletChooseClient(LoginRequiredMixin, View):

    def get(self,request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_form'] = FindClientForm()
        return render(request,'production/activate_tablet_choose_client.html', context) #placeholder

class AddClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        context['add_client_form'] = ClientRegistrationForm()
        context['all_timezones'] = pytz.all_timezones
        return render(request,'production/care_portal.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        add_client_form = ClientRegistrationForm(request.POST,request.FILES)
        context['add_client_form'] = add_client_form
        client_email = add_client_form.data['email']
        if add_client_form.is_valid():
            first_name = add_client_form.cleaned_data['first_name']
            last_name = add_client_form.cleaned_data['last_name']
            middle_name = add_client_form.cleaned_data['middle_name']
            gender = add_client_form.cleaned_data['gender']
            date_of_birth = add_client_form.cleaned_data['date_of_birth']
            phone_number = add_client_form.cleaned_data['phone_number']
            secondary_phone_number = add_client_form.cleaned_data['secondary_phone_number']
            email = add_client_form.cleaned_data['email']
            address = add_client_form.cleaned_data['address']
            city = add_client_form.cleaned_data['city']
            state = add_client_form.cleaned_data['state']
            zip_code = add_client_form.cleaned_data['zip_code']
            time_zone = add_client_form.cleaned_data['time_zone']
            profile_picture = add_client_form.cleaned_data['profile_picture']
            company = request.user.company
            #Create Client object and save
            try:
                new_client = Client(company = company,
                                    email_address = email,
                                    first_name = first_name,
                                    last_name = last_name,
                                    middle_name = middle_name,
                                    gender = gender,
                                    date_of_birth = date_of_birth,
                                    phone_number = phone_number,
                                    secondary_phone_number = secondary_phone_number,
                                    address = address,
                                    city = city,
                                    state = state,
                                    zip_code = zip_code,
                                    time_zone = time_zone
                                    )
                new_client.save()
                new_client.profile_picture = profile_picture
                new_client.save()
                messages.success(request, "Client successfully added. Add additional Details Below.")
                return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)
            except IntegrityError as e:
                messages.error(request, "Client already exists. Please enter a new client.")
        return redirect('add_client')

    def parse_date(self,client_birthday):
        caregiver_birthday = client_birthday.date()
        output_month = client_birthday.month
        output_day = client_birthday.day
        output_year = client_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

class EditChooseClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_form'] = FindClientForm()
        return render(request,'production/edit_choose_client.html', context)

class EditClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        find_client_form = FindClientForm(request.GET)
        context['all_timezones'] = pytz.all_timezones
        if find_client_form.is_valid():
            client_email = find_client_form.cleaned_data['client_email']
            client = Client.objects.get(company=current_company, email_address=client_email)
            #initialize client form
            edit_client_form = EditClientDetailsForm(initial=
            {
                'first_name': client.first_name,
                'last_name': client.last_name,
                'middle_name': client.middle_name,
                'gender': client.gender,
                'date_of_birth': self.parse_date(client.date_of_birth),
                'phone_number': client.phone_number,
                'secondary_phone_number': client.secondary_phone_number,
                'email': client.email_address,
                'address': client.address,
                'city': client.city,
                'state': client.state,
                'zip_code': client.zip_code,
                'time_zone': client.time_zone,
                'profile_picture': client.profile_picture
            })
            context['edit_client_form'] = edit_client_form
            #initialize family contact forms
            family_details = client.family_contacts.filter(is_active=True)
            provider_details = client.provider.filter(is_active=True)
            pharmacy_details = client.pharmacy.filter(is_active=True)
            payer_details = client.payer.filter(is_active=True)
            context["client_email"] = client_email
            context["family_details"] = family_details
            context["provider_details"] = provider_details
            context["pharmacy_details"] = pharmacy_details
            context["payer_details"] = payer_details
            #Details forms
            context["family_details_form"] = FamilyDetailsForm()
            context["delete_family_details_form"] = DeleteFamilyDetailsForm()
            context["provider_details_form"] = ProviderDetailsForm()
            context["pharmacy_details_form"] = PharmacyDetailsForm()
            #Deletion forms
            context["payer_details_form"] = PayerDetailsForm()
            context["delete_provider_details_form"] = DeleteProviderDetailsForm()
            context["delete_pharmacy_details_form"] = DeletePharmacyDetailsForm()
            context["delete_payer_details_form"] = DeletePayerDetailsForm()
            #Client Criteria map
            client_match_categories = ClientMatchCategory.objects.all()
            client_match_criteria = ClientMatchCriteria.objects.filter(is_default=True) | ClientMatchCriteria.objects.filter(company=current_company)
            client_criteria_map = ClientCriteriaMap.objects.filter(company=current_company,client=client)
            client_certification_map = ClientCertificationMap.objects.filter(company=current_company,client=client)
            client_transfer_map = ClientTransferMap.objects.filter(company=current_company,client=client)
            criteria_map = self.make_criteria_map(client_match_categories,client_match_criteria,client_criteria_map,current_company,client)
            certification_map = self.make_certification_map(client_match_categories,client_match_criteria,client_certification_map,current_company,client)
            transfer_map = self.make_transfer_map(client_match_categories,client_match_criteria,client_transfer_map,current_company,client)
            context['criteria_map'] = criteria_map
            context['certification_map'] = certification_map
            context['transfer_map'] = transfer_map
        return render(request,'production/edit_client.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_client_form = EditClientDetailsForm(request.POST, request.FILES)
        client_email = edit_client_form.data['email']
        context['all_timezones'] = pytz.all_timezones
        if edit_client_form.is_valid():
            try:
                client_email = edit_client_form.cleaned_data['email']
                client = Client.objects.get(company=current_company, email_address=client_email)
                client.first_name = edit_client_form.cleaned_data['first_name']
                client.last_name = edit_client_form.cleaned_data['last_name']
                client.middle_name = edit_client_form.cleaned_data['middle_name']
                client.gender = edit_client_form.cleaned_data['gender']
                client.date_of_birth = edit_client_form.cleaned_data['date_of_birth']
                client.phone_number = edit_client_form.cleaned_data['phone_number']
                client.secondary_phone_number = edit_client_form.cleaned_data['secondary_phone_number']
                client.email_address = edit_client_form.cleaned_data['email']
                client.address = edit_client_form.cleaned_data['address']
                client.city = edit_client_form.cleaned_data['city']
                client.state = edit_client_form.cleaned_data['state']
                client.zip_code = edit_client_form.cleaned_data['zip_code']
                client.time_zone = edit_client_form.cleaned_data['time_zone']
                if edit_client_form.cleaned_data['profile_picture'] != None and client.profile_picture != edit_client_form.cleaned_data['profile_picture']:
                    client.profile_picture = edit_client_form.cleaned_data['profile_picture']
                client.save()
                messages.success(request, "Client {0} {1} successfully edited!".format(client.first_name,client.last_name))
            except IntegrityError as e:
                messages.error(request, "Client already exists. Please enter a new Client.")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

    def parse_date(self,client_birthday):
        caregiver_birthday = client_birthday.date()
        output_month = client_birthday.month
        output_day = client_birthday.day
        output_year = client_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

    def make_criteria_map(self, client_match_categories,client_match_criteria,client_criteria_map,company,client):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['General', 'Pets']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = client_criteria_map.get_or_create(company=company,client=client,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

    def make_certification_map(self, client_match_categories,client_match_criteria,client_certification_map,company,client):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['Certifications']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = client_certification_map.get_or_create(company=company,client=client,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

    def make_transfer_map(self, client_match_categories,client_match_criteria,client_transfer_map,company,client):
        criteria_map = {}
        for category in client_match_categories:
            if category.category in ['Transfers']:
                criteria_map[category] = {}
                for criteria in client_match_criteria:
                    if criteria.client_match_category == category:
                        (criteria_status, created) = client_transfer_map.get_or_create(company=company,client=client,
                                                        client_match_category=category,client_match_criteria=criteria)
                        criteria_map[category][criteria] = criteria_status
                        criteria_status.save()
        return criteria_map

class AssignTasksChooseClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_form'] = FindClientForm()
        return render(request,'production/assign_tasks_choose_client.html', context)

class CreateTasks(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        activity_masters = ActivityMaster.objects.all()
        context['activity_masters'] = activity_masters
        activity_master_descriptions = map(lambda x: "{0} - {1}".format(x.activity_code,x.activity_description), activity_masters)
        context['activity_masters_descriptions'] = activity_master_descriptions
        context['create_task_form'] = CreateTaskForm()
        context['existing_tasks'] = Tasks.objects.filter(company=current_company)
        context['default_tasks'] = DefaultTasks.objects.all()
        return render(request,'production/create_tasks.html', context)

    def post(self, request):
        context = {}
        create_task_form = CreateTaskForm(request.POST)
        if create_task_form.is_valid():
            current_company = request.user.company
            task = create_task_form.cleaned_data["task"]
            activity_category_code = create_task_form.cleaned_data["sub_category"]
            new_task = Tasks(company = current_company,
                            activity_task = task,
                            activity_category_code = activity_category_code)
            new_task.save()
            context["status_message"] = "Task Added Successfully"
            messages.success(request, "Task {0} added successfully!".format(task))
        else:
            context["status_message"] = "Error Adding Task"
            messages.error(request, "Error adding task")
        return redirect("create_tasks")

class FindCaregiver(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_caregiver_form'] = FindCaregiverForm()
        return render(request,'production/CareFinder.html', context)

    def post(self, request):
        #No longer necessary - will remove later
        context = {}
        find_caregiver_form = FindCaregiverForm(request.POST)
        #context['find_caregiver_form'] = find_caregiver_form
        if find_caregiver_form.is_valid():
            client_email = find_caregiver_form.cleaned_data['client_email']
            context["client_email"] = client_email
            #url = reverse('choose_caregiver', kwargs = context)
            #return HttpResponseRedirect(url)#('choose_caregiver')
            return redirect('choose_caregiver')
        return render(request,'production/CareFinder.html', context)

class ChooseCaregiver(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        find_caregiver_form = FindCaregiverForm(request.GET)
        #context['find_caregiver_form'] = find_caregiver_form
        if find_caregiver_form.is_valid():
            client_email = find_caregiver_form.cleaned_data['client_email']
            context["client_email"] = client_email
            client = Client.objects.get(email_address=client_email)
            context["client_details"] = client
            context["assign_caregiver_form"] = AssignCaregiverForm()
            #Find which caregivers are already assigned
            assigned_caregivers = client.caregiver.all()
            context["assigned_caregivers"] = assigned_caregivers
            all_caregivers = Caregiver.objects.filter(company=current_company).order_by('last_name')
            all_caregivers = self.match_client_caregiver_criteria(all_caregivers,client,current_company)
            context['all_caregivers'] = all_caregivers
        return render(request,'production/caregiver_tables.html',context)

    @transaction.atomic
    def post(self, request):
        context = {}
        current_company = request.user.company
        assign_caregiver_form = AssignCaregiverForm(request.POST)
        if assign_caregiver_form.is_valid():
            caregiver_email = assign_caregiver_form.cleaned_data['caregiver_email']
            client_email = assign_caregiver_form.cleaned_data['client_email']
            is_unassign = assign_caregiver_form.cleaned_data['is_unassign']

            assigned_caregiver = Caregiver.objects.get(company=current_company, email_address=caregiver_email)
            assigned_client = Client.objects.get(company=current_company, email_address=client_email)
            if is_unassign == "True":
                assigned_client.caregiver.remove(assigned_caregiver)
                caregiver_schedule = CaregiverSchedule.objects.filter(company=current_company,caregiver=assigned_caregiver,client=assigned_client).delete()
            else:
                assigned_client.caregiver.add(assigned_caregiver)
            assigned_client.save()
            #GET - will replace with redirect later
            return HttpResponseRedirect(reverse('choose_caregiver') + "?client_email=" + client_email)
        else:
            return redirect('find_caregiver')

    def match_client_caregiver_criteria(self, all_caregivers, client, company):
        client_criteria = ClientCriteriaMap.objects.filter(company=company,client=client,status__in=['Y','N'])
        client_certifications = ClientCertificationMap.objects.filter(company=company,client=client,status__in=['Y','N'])
        client_transfers = ClientTransferMap.objects.filter(company=company,client=client)
        matching_caregivers = []
        for caregiver in all_caregivers:
            caregiver_criteria = CaregiverCriteriaMap.objects.filter(company=company,caregiver=caregiver)
            caregiver_certifications = CaregiverCertificationMap.objects.filter(company=company,caregiver=caregiver)
            caregiver_transfers = CaregiverTransferMap.objects.filter(company=company,caregiver=caregiver)
            (criteria_score, criteria_does_match) = self.criteria_match(client_criteria,caregiver_criteria)
            (certification_score, certification_does_match) = self.criteria_match(client_certifications,caregiver_certifications)
            (transfer_score, transfer_does_match) = self.transfer_match(client_transfers, caregiver_transfers)
            if (criteria_does_match and certification_does_match and transfer_does_match):
                matching_caregivers.append((caregiver,criteria_score + certification_score + transfer_score))
        matching_caregivers.sort(key=lambda x: x[1], reverse=True)
        matching_caregivers = map(lambda x: x[0], matching_caregivers)
        return matching_caregivers

    def criteria_match(self, client_criteria_map, caregiver_criteria_map):
        score = 0
        does_match = True
        print(len(client_criteria_map))
        print(len(caregiver_criteria_map))
        for criteria in client_criteria_map:
            client_match_criteria = criteria.client_match_criteria
            caregiver_criteria = None
            for i in caregiver_criteria_map:
                if i.client_match_criteria == client_match_criteria:
                    caregiver_criteria = i
            if caregiver_criteria:
                if (criteria.status == 'N'):
                    if (caregiver_criteria.status == 'Y'):
                        score += 1
                    else:
                        does_match = False
                elif (criteria.status == 'Y'):
                    if (caregiver_criteria.status == 'Y'):
                        score += 1
            else:
                if criteria.status == 'N':
                    does_match = False
        print(score,does_match)
        return(score,does_match)

    def transfer_match(self, client_transfer_map, caregiver_transfer_map):
        score = 0
        does_match = True
        for criteria in client_transfer_map:
            client_match_criteria = criteria.client_match_criteria
            client_experience = criteria.experience
            caregiver_criteria = None
            for i in caregiver_transfer_map:
                if i.client_match_criteria == client_match_criteria:
                    caregiver_criteria = i
            if caregiver_criteria:
                caregiver_experience = caregiver_criteria.experience
                if caregiver_experience != None and client_experience != None and caregiver_experience >= client_experience:
                    score += 1
                else:
                    does_match = False
            else:
                if client_experience != None and client_experience > 1:
                    does_match = False
        return(score,does_match)

class AssignTasks(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        find_client_form = FindClientForm(request.GET)
        if find_client_form.is_valid():
            #Get all default tasks and Company specific tasks
            existing_tasks = Tasks.objects.filter(company=current_company).order_by('activity_task')
            default_tasks = DefaultTasks.objects.all().order_by('activity_task')
            all_tasks = []
            for i in existing_tasks:
                all_tasks.append(i)
            for i in default_tasks:
                all_tasks.append(i)
            context["all_tasks"] = all_tasks
            #Populate client email
            client_email = find_client_form.cleaned_data['client_email']
            context["client_email"] = client_email
            #Get Form
            context["assign_task_form"] = AssignTaskForm()
            #Get Delete Task Form
            context["delete_task_form"] = DeleteTaskForm()
            #Get Edit Task Form
            context["edit_task_form"] = EditTaskForm()
            #Get Schedule for Client
            current_client = Client.objects.get(company=current_company,email_address=client_email)
            client_id = current_client.id
            context["client_id"] = client_id
            client_schedule = TaskSchedule.objects.filter(company=current_company,client=current_client)
            context["client_schedule"] = client_schedule
            return render(request,'production/assign_tasks.html',context)
        else:
            return redirect('assign_choose_client')

    @transaction.atomic
    def post(self, request):
        context = {}
        current_company = request.user.company
        assign_task_form = AssignTaskForm(request.POST, request.FILES)
        print("ENTERED TASK POST")
        print(request.POST)
        print(request.FILES)
        #Populated here for redirect incase form is not valid
        client_email = assign_task_form.data["client_email"]
        if assign_task_form.is_valid():
            #get data from form
            client_email = assign_task_form.cleaned_data["client_email"]
            client = Client.objects.get(company=current_company,email_address=client_email)
            task = assign_task_form.cleaned_data["task"]
            task_type = assign_task_form.cleaned_data["task_type"]
            start_date = assign_task_form.cleaned_data["start_date"]
            end_date = assign_task_form.cleaned_data["end_date"]
            start_hour = assign_task_form.cleaned_data["start_hour"]
            start_minute = assign_task_form.cleaned_data["start_minute"]
            end_hour = assign_task_form.cleaned_data["end_hour"]
            end_minute = assign_task_form.cleaned_data["end_minute"]
            description = assign_task_form.cleaned_data["description"]
            link = assign_task_form.cleaned_data["link"]
            #attachments = assign_task_form.cleaned_data["attachment"]
            attachments = request.FILES.getlist('attachment')
            start_time = ""
            end_time = ""
            if start_hour != "" and start_minute != "":
                start_time = "{0}:{1}".format(str(start_hour),str(start_minute))
            if end_hour != "" and end_minute != "":
                end_time = "{0}:{1}".format(str(end_hour),str(end_minute))
            #save task header
            new_task_header = TaskHeader(company=current_company,
                                            client=client,
                                            activity_task=task,
                                            start_date = start_date,
                                            end_date = end_date,
                                            task_type = task_type,
                                            start_time = start_time,
                                            end_time = end_time,
                                            description = description,
                                            link = link)
            new_task_header.save()
            #populate task schedule
            current_user = request.user
            if task_type == "One Time":
                self.save_one_time_task(new_task_header, attachments, current_user)
            if task_type == "Daily":
                self.save_daily_task(new_task_header, attachments, current_user)
            if task_type == "Weekly":
                self.save_weekly_task(new_task_header, attachments, current_user)
            if task_type == "Bi-Weekly":
                self.save_bi_weekly_task(new_task_header, attachments, current_user)
            if task_type == "Monthly":
                self.save_monthly_task(new_task_header, attachments, current_user)
            if task_type == "Yearly":
                self.save_yearly_task(new_task_header, attachments, current_user)
            messages.success(request, "Assigned task {0} to client {1} {2}".format(task, client.first_name, client.last_name))
        #Almost identical to GET, except don't have the find client form in context,
        #instead, just use the client email from POST
        existing_tasks = Tasks.objects.filter(company=current_company).order_by('activity_task')
        default_tasks = DefaultTasks.objects.all().order_by('activity_task')
        all_tasks = []
        for i in existing_tasks:
            all_tasks.append(i)
        for i in default_tasks:
            all_tasks.append(i)
        context["all_tasks"] = all_tasks
        #Populate client email
        context["client_email"] = client_email
        #Get Form
        context["assign_task_form"] = AssignTaskForm()
        #Get Delete Task Form
        context["delete_task_form"] = DeleteTaskForm()
        #Get Schedule for Client
        current_client = Client.objects.get(company=current_company,email_address=client_email)
        client_schedule = TaskSchedule.objects.filter(company=current_company,client=current_client)
        context["client_schedule"] = client_schedule
        return render(request,'production/assign_tasks.html',context)

    def save_task_attachments(self, new_task_header, attachments, current_user, schedule_entry):
        for uploaded_file in attachments:
            task_attachment = TaskAttachment(company=new_task_header.company,
                                            client=new_task_header.client,
                                            user=current_user,
                                            task_schedule=schedule_entry,
                                            attachment=uploaded_file)
            task_attachment.save()

    def save_existing_task_attachments(self, uploaded_task_attachments, schedule_entry):
        for uploaded_attachment in uploaded_task_attachments:
            new_task_attachment = TaskAttachment(company = uploaded_attachment.company,
                                                client = uploaded_attachment.client,
                                                user = uploaded_attachment.user,
                                                task_schedule = schedule_entry,
                                                attachment = uploaded_attachment.attachment)
            new_task_attachment.save()

    def save_and_return_task_attachments(self, new_task_header, attachments, current_user, schedule_entry):
        uploaded_task_attachments = []
        for uploaded_file in attachments:
            task_attachment = TaskAttachment(company=new_task_header.company,
                                            client=new_task_header.client,
                                            user=current_user,
                                            task_schedule=schedule_entry,
                                            attachment=uploaded_file)
            task_attachment.save()
            uploaded_task_attachments.append(task_attachment)
        return uploaded_task_attachments

    def save_task_link(self, new_task_header, link, current_user, schedule_entry):
        #will change to support multiple links later
        task_link = TaskLink(company=new_task_header.company,
                                client=new_task_header.client,
                                user=current_user,
                                task_schedule=schedule_entry,
                                task_url=link)
        task_link.save()
        print("Saved task link")

    def save_one_time_task(self, new_task_header, attachments, current_user):
        schedule_entry = TaskSchedule(company=new_task_header.company,
                                        client=new_task_header.client,
                                        activity_task=new_task_header.activity_task,
                                        date=new_task_header.start_date,
                                        start_time=new_task_header.start_time,
                                        end_time=new_task_header.end_time,
                                        description = new_task_header.description,
                                        link = new_task_header.link,
                                        task_header = new_task_header)
        schedule_entry.save()
        self.save_task_attachments(new_task_header, attachments, current_user, schedule_entry)
        link = new_task_header.link
        if link != None and link!= "":
            self.save_task_link(new_task_header, link, current_user, schedule_entry)

    def save_daily_task(self, new_task_header, attachments, current_user):
        start_date = new_task_header.start_date
        end_date = new_task_header.end_date
        date_range_num = end_date - start_date
        uploaded_task_attachments = []
        for i in range(date_range_num.days + 1):
            new_date = (start_date + datetime.timedelta(days=i)).date()
            schedule_entry = TaskSchedule(company=new_task_header.company,
                                            client=new_task_header.client,
                                            activity_task=new_task_header.activity_task,
                                            date=new_date,
                                            start_time=new_task_header.start_time,
                                            end_time=new_task_header.end_time,
                                            description = new_task_header.description,
                                            link = new_task_header.link,
                                            task_header = new_task_header)
            schedule_entry.save()
            if len(uploaded_task_attachments)==0:
                uploaded_task_attachments = self.save_and_return_task_attachments(new_task_header, attachments, current_user, schedule_entry)
            else:
                self.save_existing_task_attachments(uploaded_task_attachments, schedule_entry)
            link = new_task_header.link
            if link != None and link!= "":
                self.save_task_link(new_task_header, link, current_user, schedule_entry)

    def save_weekly_task(self, new_task_header, attachments, current_user):
        start_date = new_task_header.start_date
        current_date = start_date
        end_date = new_task_header.end_date
        delta = datetime.timedelta(days=7) #per Week
        uploaded_task_attachments = []
        while current_date <= end_date:
            new_date = current_date
            schedule_entry = TaskSchedule(company=new_task_header.company,
                                            client=new_task_header.client,
                                            activity_task=new_task_header.activity_task,
                                            date=new_date,
                                            start_time=new_task_header.start_time,
                                            end_time=new_task_header.end_time,
                                            description = new_task_header.description,
                                            link = new_task_header.link,
                                            task_header = new_task_header)
            schedule_entry.save()
            if len(uploaded_task_attachments)==0:
                uploaded_task_attachments = self.save_and_return_task_attachments(new_task_header, attachments, current_user, schedule_entry)
            else:
                self.save_existing_task_attachments(uploaded_task_attachments, schedule_entry)
            link = new_task_header.link
            if link != None and link!= "":
                self.save_task_link(new_task_header, link, current_user, schedule_entry)
            current_date += delta

    def save_bi_weekly_task(self, new_task_header, attachments, current_user):
        start_date = new_task_header.start_date
        current_date = start_date
        end_date = new_task_header.end_date
        delta = datetime.timedelta(days=14) #per Week
        uploaded_task_attachments = []
        while current_date <= end_date:
            new_date = current_date
            schedule_entry = TaskSchedule(company=new_task_header.company,
                                            client=new_task_header.client,
                                            activity_task=new_task_header.activity_task,
                                            date=new_date,
                                            start_time=new_task_header.start_time,
                                            end_time=new_task_header.end_time,
                                            description = new_task_header.description,
                                            link = new_task_header.link,
                                            task_header = new_task_header)
            schedule_entry.save()
            if len(uploaded_task_attachments)==0:
                uploaded_task_attachments = self.save_and_return_task_attachments(new_task_header, attachments, current_user, schedule_entry)
            else:
                self.save_existing_task_attachments(uploaded_task_attachments, schedule_entry)
            link = new_task_header.link
            if link != None and link!= "":
                self.save_task_link(new_task_header, link, current_user, schedule_entry)
            current_date += delta

    def save_monthly_task(self, new_task_header, attachments, current_user):
        start_date = new_task_header.start_date
        current_date = start_date
        end_date = new_task_header.end_date
        delta = relativedelta.relativedelta(months=1) #per Month
        uploaded_task_attachments = []
        while current_date <= end_date:
            new_date = current_date
            schedule_entry = TaskSchedule(company=new_task_header.company,
                                            client=new_task_header.client,
                                            activity_task=new_task_header.activity_task,
                                            date=new_date,
                                            start_time=new_task_header.start_time,
                                            end_time=new_task_header.end_time,
                                            description = new_task_header.description,
                                            link = new_task_header.link,
                                            task_header = new_task_header)
            schedule_entry.save()
            if len(uploaded_task_attachments)==0:
                uploaded_task_attachments = self.save_and_return_task_attachments(new_task_header, attachments, current_user, schedule_entry)
            else:
                self.save_existing_task_attachments(uploaded_task_attachments, schedule_entry)
            link = new_task_header.link
            if link != None and link!= "":
                self.save_task_link(new_task_header, link, current_user, schedule_entry)
            current_date += delta

    def save_yearly_task(self, new_task_header, attachments, current_user):
        start_date = new_task_header.start_date
        current_date = start_date
        end_date = new_task_header.end_date
        delta = relativedelta.relativedelta(months=12) #per Year
        uploaded_task_attachments = []
        while current_date <= end_date:
            new_date = current_date
            schedule_entry = TaskSchedule(company=new_task_header.company,
                                            client=new_task_header.client,
                                            activity_task=new_task_header.activity_task,
                                            date=new_date,
                                            start_time=new_task_header.start_time,
                                            end_time=new_task_header.end_time,
                                            description = new_task_header.description,
                                            link = new_task_header.link,
                                            task_header = new_task_header)
            schedule_entry.save()
            if len(uploaded_task_attachments)==0:
                uploaded_task_attachments = self.save_and_return_task_attachments(new_task_header, attachments, current_user, schedule_entry)
            else:
                self.save_existing_task_attachments(uploaded_task_attachments, schedule_entry)
            link = new_task_header.link
            if link != None and link!= "":
                self.save_task_link(new_task_header, link, current_user, schedule_entry)
            current_date += delta

class ViewIncidentsByClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        find_client_form = FindClientForm(request.GET)
        if find_client_form.is_valid():
            client_email = find_client_form.cleaned_data['client_email']
            client = Client.objects.get(company=current_company, email_address = client_email)
            client_incidents = IncidentReport.objects.filter(company=current_company, client=client).order_by('incident_timestamp')
            client_timezone = pytz.timezone(client.time_zone)
            for client_incident in client_incidents:
                client_incident.incident_timestamp = (client_incident.incident_timestamp.astimezone(client_timezone)).replace(tzinfo=None)
            context['client_incidents'] = client_incidents
        return render(request,'production/view_client_incidents.html', context)

class ChooseViewClientIncidents(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_form'] = FindClientForm()
        return render(request,'production/choose_view_client_incidents.html', context)

@login_required
def get_client_with_email(request):
    if request.method == 'GET':
        context = {}
        email = request.GET.get('email_data')
        current_company = request.user.company
        client = Client.objects.get(company=current_company,email_address = email)
        name = '{0} {1}'.format(client.first_name, client.last_name)
        address = '{0}, {1} {2} {3}'.format(client.address, client.city, client.state, client.zip_code)
        phone_number = client.phone_number
        raw_dob = client.date_of_birth
        date_of_birth = '{0}/{1}/{2}'.format(raw_dob.month,raw_dob.day,raw_dob.year)
        gender = client.gender
        client_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'date_of_birth': date_of_birth,
                        'gender': gender,
                        'email_address': email}
        if client.profile_picture:
            client_data['profile_picture'] = client.profile_picture.url
        context["client_data"] = client_data
        return HttpResponse(json.dumps(client_data), content_type="application/json")

@login_required
def get_task_with_id(request):
    if request.method == 'GET':
        context = {}
        task_id = request.GET.get('task_id')
        current_company = request.user.company
        current_task = TaskSchedule.objects.get(company=current_company,id = task_id)
        client = current_task.client
        task_name = current_task.activity_task
        start_time = current_task.start_time
        end_time = current_task.end_time
        start_hour = ""
        start_minute = ""
        end_hour = ""
        end_minute = ""
        if start_time:
            start_hour = start_time.split(":")[0]
            start_minute = start_time.split(":")[1]
        if end_time:
            end_hour = end_time.split(":")[0]
            end_minute = end_time.split(":")[1]
        description = current_task.description
        link = current_task.link
        attachment = current_task.attachment
        comments = list(map(lambda x: [x.comment,
                                        '{0} {1}'.format(x.caregiver.first_name,x.caregiver.last_name),
                                        '{0}/{1}/{2} {3}'.format(
                                            convert_to_client_timezone(x.created,client).month,
                                            convert_to_client_timezone(x.created,client).day,
                                            convert_to_client_timezone(x.created,client).year,
                                            convert_to_client_timezone(x.created,client).time())],
                                        TaskComment.objects.filter(task_schedule=current_task)))
        attachments = list(map(lambda x: [x.attachment.url,
                                        '{0} {1}'.format(x.user.first_name,x.user.last_name),
                                        '{0}/{1}/{2} {3}'.format(
                                            convert_to_client_timezone(x.created,client).month,
                                            convert_to_client_timezone(x.created,client).day,
                                            convert_to_client_timezone(x.created,client).year,
                                            convert_to_client_timezone(x.created,client).time()
                                        )],
                                TaskAttachment.objects.filter(task_schedule=current_task)))
        links = list(map(lambda x: [x.task_url,
                                        '{0} {1}'.format(x.user.first_name,x.user.last_name),
                                        '{0}/{1}/{2} {3}'.format(
                                            convert_to_client_timezone(x.created,client).month,
                                            convert_to_client_timezone(x.created,client).day,
                                            convert_to_client_timezone(x.created,client).year,
                                            convert_to_client_timezone(x.created,client).time()
                                        )],
                                TaskLink.objects.filter(task_schedule=current_task)))
        status = ""
        if current_task.pending:
            status = "pending"
        elif current_task.in_progress:
            status = "in_progress"
        elif current_task.complete:
            status = "complete"
        elif current_task.cancelled:
            status = "cancelled"
        task_data = {'task_id': task_id,
                    'task_name': task_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'start_hour': start_hour,
                    'start_minute': start_minute,
                    'end_hour': end_hour,
                    'end_minute': end_minute,
                    'description': description,
                    'comments': comments,
                    'attachments': attachments,
                    'links': links,
                    'status': status
                    }
        if attachment != "":
            task_data['attachment'] = attachment.url
        #Get header info if header exists
        if current_task.task_header:
            task_data['task_type'] = current_task.task_header.task_type
            task_data['start_date'] = '{0}/{1}/{2}'.format(current_task.task_header.start_date.month,
                                                        current_task.task_header.start_date.day,
                                                        current_task.task_header.start_date.year)
            task_data['end_date'] = '{0}/{1}/{2}'.format(current_task.task_header.end_date.month,
                                                        current_task.task_header.end_date.day,
                                                        current_task.task_header.end_date.year)
        return HttpResponse(json.dumps(task_data), content_type="application/json")

def convert_to_client_timezone(client_timestamp, client):

    client_timezone = pytz.timezone(client.time_zone)
    new_timestamp = (client_timestamp.astimezone(client_timezone))
    return new_timestamp

@login_required
@transaction.atomic
def edit_task_with_id(request):
    if request.method == 'POST':
        context = {}
        company = request.user.company
        edit_task_form = EditTaskForm(request.POST, request.FILES)
        client_id = request.POST.get('client_id')
        if edit_task_form.is_valid():
            task_id = edit_task_form.cleaned_data["task_id"]
            client_id = edit_task_form.cleaned_data["client_id"]
            current_client = Client.objects.get(company=company, id=client_id)
            client_email = current_client.email_address
            current_task = TaskSchedule.objects.get(company=company,client=current_client, id=task_id)
            description = edit_task_form.cleaned_data["description"]
            start_hour = edit_task_form.cleaned_data["start_hour"]
            end_hour = edit_task_form.cleaned_data["end_hour"]
            start_minute = edit_task_form.cleaned_data["start_minute"]
            end_minute = edit_task_form.cleaned_data["end_minute"]
            attachments = request.FILES.getlist('attachment')
            start_time = ""
            end_time = ""
            if start_hour != "" and start_minute != "":
                start_time = "{0}:{1}".format(str(start_hour),str(start_minute))
            if end_hour != "" and end_minute != "":
                end_time = "{0}:{1}".format(str(end_hour),str(end_minute))
            current_task.description = description
            current_task.start_time = start_time
            current_task.end_time = end_time
            current_task.save()
            for uploaded_attachment in attachments:
                new_task_attachment = TaskAttachment(company = company,
                                                    client = current_client,
                                                    user = request.user,
                                                    task_schedule = current_task,
                                                    attachment = uploaded_attachment)
                new_task_attachment.save()
            messages.success(request, "Successfully Edited Task!")
            return HttpResponseRedirect(reverse('assign_tasks') + "?client_email=" + client_email)
    messages.error(request, "Error Editing Task")
    current_client = Client.objects.get(company=company, id=client_id)
    client_email = current_client.email_address
    return HttpResponseRedirect(reverse('assign_tasks') + "?client_email=" + client_email)

@login_required
def delete_task_with_id(request):
    if request.method == 'POST':
        context = {}
        company = request.user.company
        task_id = request.POST.get('task_id')
        current_task = TaskSchedule.objects.get(company=company, id = task_id)
        current_task.delete()
        return HttpResponse("Delete Successful")

@login_required
def delete_recurring_task_with_id(request):
    if request.method == 'POST':
        context = {}
        company = request.user.company
        task_id = request.POST.get('task_id')
        current_task = TaskSchedule.objects.get(company=company, id = task_id)
        task_header = current_task.task_header
        all_recurring_task_ids = []
        if task_header != None:
            all_recurring_tasks = TaskSchedule.objects.filter(company=company, task_header=task_header)
            all_recurring_task_ids = list(map(lambda x: x.id, all_recurring_tasks))
            for recurring_task in all_recurring_tasks:
                recurring_task.delete()
        return HttpResponse(json.dumps(all_recurring_task_ids),content_type="application/json")

@login_required
@transaction.atomic
def post_family_details(request):
    if request.method == 'POST':
        context = {}
        company = request.user.company
        family_details_form = FamilyDetailsForm(request.POST,request.FILES)
        if family_details_form.is_valid():
            try:
                first_name = family_details_form.cleaned_data['first_name']
                last_name = family_details_form.cleaned_data['last_name']
                relationship = family_details_form.cleaned_data['relationship']
                phone_number = family_details_form.cleaned_data['phone_number']
                email = family_details_form.cleaned_data['email']
                address = family_details_form.cleaned_data['address']
                city = family_details_form.cleaned_data['city']
                state = family_details_form.cleaned_data['state']
                zip_code = family_details_form.cleaned_data['zip_code']
                power_of_attorney = family_details_form.cleaned_data['power_of_attorney']
                profile_picture = family_details_form.cleaned_data['profile_picture']
                password = family_details_form.cleaned_data['password']
                family_id = family_details_form.cleaned_data['family_id']
                print(power_of_attorney)
                #Create family user auth model and save
                if(family_id==None):
                    #check if there is an existing soft-deleted user
                    existing_user = User.objects.filter(company=company,username=email,email=email)
                    if(existing_user):
                        existing_user = existing_user[0]
                        client_email = family_details_form.cleaned_data['client_email']
                        assigned_client = Client.objects.get(company=company,email_address=client_email)
                        existing_family_contact = FamilyContact.objects.get(company=request.user.company,user=existing_user)
                        if assigned_client.family_contacts.filter(company=company,id=existing_family_contact.id):
                            #update User Auth object
                            existing_user.username=email
                            existing_user.email=email
                            existing_user.first_name=first_name
                            existing_user.last_name=last_name
                            existing_user.is_active = True
                            existing_user.save()
                            #update Family Contact object
                            existing_family_contact.email_address = email
                            existing_family_contact.first_name = first_name
                            existing_family_contact.last_name = last_name
                            existing_family_contact.relationship = relationship
                            existing_family_contact.phone_number = phone_number
                            existing_family_contact.address = address
                            existing_family_contact.city = city
                            existing_family_contact.state = state
                            existing_family_contact.zip_code = zip_code
                            existing_family_contact.power_of_attorney = power_of_attorney
                            existing_family_contact.is_active = True
                            if profile_picture is not None:
                                existing_family_contact.profile_picture = profile_picture
                            existing_family_contact.save()
                            messages.success(request, "Successfully added family contact {0} {1}!".format(first_name,last_name))
                        else:
                            messages.error(request, "Family member already exists. Please enter new family member.")
                    else:
                        new_user = User.objects.create_user(username=email,
                                                            email=email,
                                                            first_name=first_name,
                                                            last_name=last_name,
                                                            password=password,
                                                            company=company)
                        new_user.save()
                        #Create family object and save
                        family_contact = FamilyContact(user = new_user,
                                                  company=company,
                                                  email_address = email,
                                                  first_name = first_name,
                                                  last_name = last_name,
                                                  relationship = relationship,
                                                  phone_number = phone_number,
                                                  address = address,
                                                  city = city,
                                                  state = state,
                                                  zip_code = zip_code,
                                                  power_of_attorney = power_of_attorney
                                                  )
                        family_contact.save()
                        if profile_picture is not None:
                            family_contact.profile_picture = profile_picture
                        family_contact.save()
                        #Add new user to UserRoles with CAREGIVER Role
                        new_role = UserRoles(company=company,
                                                user=new_user,
                                                role='FAMILYUSER')
                        new_role.save()
                        #Add family user to client
                        client_email = family_details_form.cleaned_data['client_email']
                        assigned_client = Client.objects.get(company=company,email_address=client_email)
                        assigned_client.family_contacts.add(family_contact)
                        assigned_client.save()
                        messages.success(request, "Successfully added family contact {0} {1}!".format(first_name,last_name))
                else:
                    existing_family_member = FamilyContact.objects.get(company=request.user.company,id=family_id)
                    existing_user = existing_family_member.user
                    #update User Auth object
                    existing_user.username=email
                    existing_user.email=email
                    existing_user.first_name=first_name
                    existing_user.last_name=last_name
                    existing_user.save()
                    #update Family Contact object
                    existing_family_member.email_address = email
                    existing_family_member.first_name = first_name
                    existing_family_member.last_name = last_name
                    existing_family_member.relationship = relationship
                    existing_family_member.phone_number = phone_number
                    existing_family_member.address = address
                    existing_family_member.city = city
                    existing_family_member.state = state
                    existing_family_member.zip_code = zip_code
                    existing_family_member.power_of_attorney = power_of_attorney
                    if profile_picture is not None:
                        existing_family_member.profile_picture = profile_picture
                    existing_family_member.save()
                    messages.success(request, "Edited family contact {0} {1}!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Family member already exists. Please enter new family member.")
        #even if form is invalid, client_email still retrieved
        client_email = request.POST.get('client_email')
        #next 4 lines used for AJAX version
        #assigned_client = Client.objects.get(email_address=client_email)
        #family_contacts = assigned_client.family_contacts.all()
        #family_contacts = serializers.serialize('json',family_contacts)
        #return HttpResponse(json.dumps(family_contacts),content_type="application/json")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)


@login_required
@transaction.atomic
def post_provider_details(request):

    if request.method == 'POST':
        context = {}
        company = request.user.company
        provider_details_form = ProviderDetailsForm(request.POST,request.FILES)
        if provider_details_form.is_valid():
            try:
                first_name = provider_details_form.cleaned_data['first_name']
                last_name = provider_details_form.cleaned_data['last_name']
                speciality = provider_details_form.cleaned_data['speciality']
                phone_number = provider_details_form.cleaned_data['phone_number']
                secondary_phone_number = provider_details_form.cleaned_data['secondary_phone_number']
                email = provider_details_form.cleaned_data['email']
                password = provider_details_form.cleaned_data['password']
                provider_id = provider_details_form.cleaned_data['provider_id']
                if(provider_id is None):
                    #check if there is an existing soft-deleted user
                    existing_user = User.objects.filter(company=company,username=email,email=email)
                    if(existing_user):
                        existing_user = existing_user[0]
                        client_email = provider_details_form.cleaned_data['client_email']
                        assigned_client = Client.objects.get(company=company,email_address=client_email)
                        existing_provider = Provider.objects.get(company=request.user.company,user=existing_user)
                        if assigned_client.provider.filter(company=company,id=existing_provider.id):
                            #update User Auth object
                            existing_user.username=email
                            existing_user.email=email
                            existing_user.first_name=first_name
                            existing_user.last_name=last_name
                            existing_user.is_active = True
                            existing_user.save()
                            #update Provider object
                            existing_provider.email_address = email
                            existing_provider.first_name = first_name
                            existing_provider.last_name = last_name
                            existing_provider.speciality = speciality
                            existing_provider.phone_number = phone_number
                            existing_provider.secondary_phone_number = secondary_phone_number
                            existing_provider.is_active = True
                            existing_provider.save()
                            messages.success(request, "Added provider {0} {1}!".format(first_name,last_name))
                        else:
                            messages.error(request, "Provider already exists. Please enter new Provider.")
                    else:
                        new_user = User.objects.create_user(username=email,
                                                            email=email,
                                                            first_name=first_name,
                                                            last_name=last_name,
                                                            password=password,
                                                            company=company)
                        new_user.save()
                        #Create Provider object and save
                        provider_user = Provider(user = new_user,
                                                  company=company,
                                                  email_address = email,
                                                  first_name = first_name,
                                                  last_name = last_name,
                                                  speciality = speciality,
                                                  phone_number = phone_number,
                                                  secondary_phone_number = secondary_phone_number
                                                  )
                        provider_user.save()
                        #Add new user to UserRoles with PROVIDER Role
                        new_role = UserRoles(company=company,
                                                user=new_user,
                                                role='PROVIDERUSER')
                        new_role.save()
                        #Add Provider user to client
                        client_email = provider_details_form.cleaned_data['client_email']
                        assigned_client = Client.objects.get(company=company,email_address=client_email)
                        assigned_client.provider.add(provider_user)
                        assigned_client.save()
                        messages.success(request, "Added provider {0} {1}!".format(first_name,last_name))
                else:
                    existing_provider = Provider.objects.get(company=request.user.company,id=provider_id)
                    existing_user = existing_provider.user
                    #update User Auth object
                    existing_user.username=email
                    existing_user.email=email
                    existing_user.first_name=first_name
                    existing_user.last_name=last_name
                    existing_user.save()
                    #update Provider object
                    existing_provider.email_address = email
                    existing_provider.first_name = first_name
                    existing_provider.last_name = last_name
                    existing_provider.speciality = speciality
                    existing_provider.phone_number = phone_number
                    existing_provider.secondary_phone_number = secondary_phone_number
                    existing_provider.save()
                    messages.success(request, "Edited provider {0} {1}!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Provider already exists. Please enter new Provider.")
        else:
            print(provider_details_form.errors)
        client_email = request.POST.get('client_email')
        #BELOW: AJAX
        #assigned_client = Client.objects.get(company=request.user.company,email_address=client_email)
        #providers = assigned_client.provider.all()
        #providers = serializers.serialize('json',providers)
        #return HttpResponse(json.dumps(providers),content_type="application/json")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
@transaction.atomic
def post_pharmacy_details(request):

    if request.method == 'POST':
        context = {}
        company = request.user.company
        pharmacy_details_form = PharmacyDetailsForm(request.POST,request.FILES)
        if pharmacy_details_form.is_valid():
            try:
                pharmacy_name = pharmacy_details_form.cleaned_data['pharmacy_name']
                contact_name = pharmacy_details_form.cleaned_data['contact_name']
                phone_number = pharmacy_details_form.cleaned_data['phone_number']
                fax_number = pharmacy_details_form.cleaned_data['fax_number']
                email = pharmacy_details_form.cleaned_data['email']
                pharmacy_id = pharmacy_details_form.cleaned_data['pharmacy_id']
                client_email = pharmacy_details_form.cleaned_data['client_email']
                address = pharmacy_details_form.cleaned_data['address']
                city = pharmacy_details_form.cleaned_data['city']
                state = pharmacy_details_form.cleaned_data['state']
                zip_code = pharmacy_details_form.cleaned_data['zip_code']
                if(pharmacy_id is None):
                    #Create family object and save
                    pharmacy = Pharmacy(company=company,
                                          email_address = email,
                                          name = pharmacy_name,
                                          contact_name = contact_name,
                                          phone_number = phone_number,
                                          fax_number = fax_number,
                                          address = address,
                                          city = city,
                                          state = state,
                                          zip_code = zip_code
                                          )
                    pharmacy.save()
                    #Add family user to client
                    client_email = pharmacy_details_form.cleaned_data['client_email']
                    assigned_client = Client.objects.get(company=company,email_address=client_email)
                    assigned_client.pharmacy.add(pharmacy)
                    assigned_client.save()
                    messages.success(request, "Added pharmacy {0}!".format(pharmacy_name))
                else:
                    existing_pharmacy = Pharmacy.objects.get(company=request.user.company,id=pharmacy_id)
                    #update Provider object
                    existing_pharmacy.email_address = email
                    existing_pharmacy.name = pharmacy_name
                    existing_pharmacy.contact_name = contact_name
                    existing_pharmacy.phone_number = phone_number
                    existing_pharmacy.fax_number = fax_number
                    existing_pharmacy.address = address
                    existing_pharmacy.city = city
                    existing_pharmacy.state = state
                    existing_pharmacy.zip_code = zip_code
                    existing_pharmacy.save()
                    messages.success(request, "Edited pharmacy {0}!".format(pharmacy_name))
            except IntegrityError as e:
                messages.error(request, "Pharmacy already exists. Please enter new pharmacy.")
        else:
            print(pharmacy_details_form.errors)
        client_email = request.POST.get('client_email')
        #BELOW: AJAX
        #assigned_client = Client.objects.get(company=request.user.company,email_address=client_email)
        #pharmacies = assigned_client.provider.all()
        #pharmacies = serializers.serialize('json',pharmacies)
        #return HttpResponse(json.dumps(pharmacies),content_type="application/json")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
@transaction.atomic
def post_payer_details(request):

    if request.method == 'POST':
        context = {}
        company = request.user.company
        payer_details_form = PayerDetailsForm(request.POST,request.FILES)
        if payer_details_form.is_valid():
            try:
                payer_name = payer_details_form.cleaned_data['payer_name']
                contact_name = payer_details_form.cleaned_data['contact_name']
                phone_number = payer_details_form.cleaned_data['phone_number']
                fax_number = payer_details_form.cleaned_data['fax_number']
                email = payer_details_form.cleaned_data['email']
                policy_start_date = payer_details_form.cleaned_data['policy_start_date']
                policy_end_date = payer_details_form.cleaned_data['policy_end_date']
                policy_number = payer_details_form.cleaned_data['policy_number']
                payer_id = payer_details_form.cleaned_data['payer_id']
                client_email = payer_details_form.cleaned_data['client_email']
                address = payer_details_form.cleaned_data['address']
                city = payer_details_form.cleaned_data['city']
                state = payer_details_form.cleaned_data['state']
                zip_code = payer_details_form.cleaned_data['zip_code']
                if(payer_id is None):
                    #Create family object and save
                    payer = Payer(company=company,
                                  email_address = email,
                                  name = payer_name,
                                  contact_name = contact_name,
                                  phone_number = phone_number,
                                  fax_number = fax_number,
                                  policy_start_date = policy_start_date,
                                  policy_end_date = policy_end_date,
                                  policy_number = policy_number,
                                  address=address,
                                  city=city,
                                  state=state,
                                  zip_code=zip_code
                                          )
                    payer.save()
                    #Add family user to client
                    client_email = payer_details_form.cleaned_data['client_email']
                    assigned_client = Client.objects.get(company=company,email_address=client_email)
                    assigned_client.payer.add(payer)
                    assigned_client.save()
                    messages.success(request, "Added payer {0}!".format(payer_name))
                else:
                    existing_payer = Payer.objects.get(company=request.user.company,id=payer_id)
                    #update Provider object
                    existing_payer.email_address = email
                    existing_payer.name = payer_name
                    existing_payer.contact_name = contact_name
                    existing_payer.phone_number = phone_number
                    existing_payer.fax_number = fax_number
                    existing_payer.policy_start_date = policy_start_date
                    existing_payer.policy_end_date = policy_end_date
                    existing_payer.policy_number = policy_number
                    existing_payer.address = address
                    existing_payer.city = city
                    existing_payer.state = state
                    existing_payer.zip_code = zip_code
                    existing_payer.save()
                    messages.success(request, "Edited payer {0}!".format(payer_name))
            except IntegrityError as e:
                messages.error(request, "Payer already exists. Please enter new payer.")
        else:
            print(payer_details_form.errors)
        client_email = request.POST.get('client_email')
        #BELOW: AJAX
        #assigned_client = Client.objects.get(company=request.user.company,email_address=client_email)
        #payers = assigned_client.payer.all()
        #payers = serializers.serialize('json',payers)
        #return HttpResponse(json.dumps(payers),content_type="application/json")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
def get_family_with_id(request):
    if request.method == 'GET':
        context = {}
        current_company = request.user.company
        family_id = request.GET.get('family_id')
        family_member = FamilyContact.objects.get(company=current_company, id=family_id)
        family_member_data = {
            'first_name': family_member.first_name,
            'last_name': family_member.last_name,
            'relationship': family_member.relationship,
            'phone_number': family_member.phone_number,
            'email_address': family_member.email_address,
            'address': family_member.address,
            'city': family_member.city,
            'state': family_member.state,
            'zip_code': family_member.zip_code,
            'power_of_attorney': family_member.power_of_attorney,
            'family_id': family_member.id
        }
        if family_member.profile_picture:
            family_member_data['profile_picture'] = family_member.profile_picture.url
        return HttpResponse(json.dumps(family_member_data), content_type="application/json")

@login_required
@transaction.atomic
def delete_family_member(request):
    if request.method == 'POST':
        try:
            current_company = request.user.company
            family_id = request.POST.get('family_id')
            client_email = request.POST.get('client_email')
            if family_id != "" and client_email != "":
                family_member = FamilyContact.objects.get(company=current_company, id=family_id)
                family_member.is_active=False
                family_user = family_member.user
                family_user.is_active=False
                family_member.save()
                family_user.save()
                messages.success(request, "Deleted family contact {0} {1}".format(family_member.first_name,family_member.last_name))
            else:
                messages.warning(request, "Did not find family contact to delete.")
        except ObjectDoesNotExist as e:
            messages.error(request, "Did not find family contact to delete.")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
def get_provider_with_id(request):
    if request.method == 'GET':
        context = {}
        current_company = request.user.company
        provider_id = request.GET.get('provider_id')
        provider = Provider.objects.get(company=current_company,id=provider_id)
        provider_data = {
            'first_name': provider.first_name,
            'last_name': provider.last_name,
            'speciality': provider.speciality,
            'phone_number': provider.phone_number,
            'secondary_phone_number': provider.secondary_phone_number,
            'email_address': provider.email_address,
            'provider_id': provider.id
        }
        return HttpResponse(json.dumps(provider_data),content_type="application/json")

@login_required
@transaction.atomic
def delete_provider(request):
    if request.method == 'POST':
        try:
            current_company = request.user.company
            provider_id = request.POST.get('provider_id')
            client_email = request.POST.get('client_email')
            if provider_id != "" and client_email != "":
                provider = Provider.objects.get(company=current_company, id=provider_id)
                provider.is_active=False
                provider_user = provider.user
                provider.is_active=False
                provider.save()
                provider_user.save()
                messages.success(request, "Deleted provider contact {0} {1}".format(provider.first_name,provider.last_name))
            else:
                messages.warning(request, "Did not find provider to delete.")
        except ObjectDoesNotExist as e:
            messages.error(request, "Did not find provider to delete.")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
def get_pharmacy_with_id(request):
    if request.method == 'GET':
        context = {}
        current_company = request.user.company
        pharmacy_id = request.GET.get('pharmacy_id')
        pharmacy = Pharmacy.objects.get(company=current_company,id=pharmacy_id)
        pharmacy_data = {
            'email': pharmacy.email_address,
            'name': pharmacy.name,
            'contact_name': pharmacy.contact_name,
            'phone_number': pharmacy.phone_number,
            'fax_number': pharmacy.fax_number,
            'pharmacy_id': pharmacy.id,
            'address' : pharmacy.address,
            'city' : pharmacy.city,
            'state' : pharmacy.state,
            'zip_code' : pharmacy.zip_code
        }
        return HttpResponse(json.dumps(pharmacy_data),content_type="application/json")


@login_required
def delete_pharmacy(request):
    if request.method == 'POST':
        try:
            current_company = request.user.company
            pharmacy_id = request.POST.get('pharmacy_id')
            client_email = request.POST.get('client_email')
            if pharmacy_id != "" and client_email != "":
                pharmacy = Pharmacy.objects.get(company=current_company, id=pharmacy_id)
                pharmacy.is_active=False
                pharmacy.save()
                messages.success(request,"Deleted pharmacy {0}".format(pharmacy.name))
            else:
                messages.warning(request,"Did not find pharmacy to delete.")
        except ObjectDoesNotExist as e:
            messages.error(request, "Did not find pharmacy to delete.")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
def get_payer_with_id(request):
    if request.method == 'GET':
        context = {}
        current_company = request.user.company
        payer_id = request.GET.get('payer_id')
        payer = Payer.objects.get(company=current_company,id=payer_id)
        payer_data = {
            'email': payer.email_address,
            'name': payer.name,
            'contact_name': payer.contact_name,
            'phone_number': payer.phone_number,
            'fax_number': payer.fax_number,
            'policy_start_date': str(payer.policy_start_date),
            'policy_end_date': str(payer.policy_end_date),
            'policy_number': payer.policy_number,
            'payer_id': payer.id,
            'address' : payer.address,
            'city' : payer.city,
            'state' : payer.state,
            'zip_code' : payer.zip_code
        }
        return HttpResponse(json.dumps(payer_data),content_type="application/json")

@login_required
def delete_payer(request):
    if request.method == 'POST':
        try:
            current_company = request.user.company
            payer_id = request.POST.get('payer_id')
            client_email = request.POST.get('client_email')
            if payer_id != "" and client_email != "":
                payer = Payer.objects.get(company=current_company, id=payer_id)
                payer.is_active=False
                payer.save()
                messages.success(request, "Deleted payor {0}".format(payer.name))
            else:
                messages.warning(request, "Did not find payor to delete.")
        except ObjectDoesNotExist as e:
            messages.warning(request, "Did not find payor to delete.")
        return HttpResponseRedirect(reverse('edit_client') + "?client_email=" + client_email)

@login_required
def get_sub_categories(request):
    if request.method == 'GET':
        context = {}
        master_code = request.GET.get('master_code')
        sub_categories = ActivitySubCategory.objects.filter(activity_code=master_code)
        sub_categories = serializers.serialize('json',sub_categories)
        return HttpResponse(json.dumps(sub_categories), content_type="application/json")

@login_required
def find_caregiver(request):
    return render(request, 'production/CareFinder.html')

@login_required
def post_criteria(request):

    if request.method == "POST":
        company = request.user.company;
        status_id = request.POST['status_id']
        status_id = status_id.split('_')[0]
        status = request.POST['status']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        criteria_map = ClientCriteriaMap.objects.get(company=company,id=status_id)
        criteria_map.status = status
        criteria_map.save()
    return HttpResponse("Changed Status")

@login_required
def post_certification(request):

    if request.method == "POST":
        company = request.user.company;
        status_id = request.POST['status_id']
        status_id = status_id.split('_')[0]
        status = request.POST['status']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        certification_map = ClientCertificationMap.objects.get(company=company,id=status_id)
        certification_map.status = status
        certification_map.save()
    return HttpResponse("Changed Status")

@login_required
def post_transfer(request):

    if request.method == "POST":
        company = request.user.company;
        experience_id = request.POST['experience_id']
        experience_id = experience_id.split('_')[0]
        experience = request.POST['experience']
        #client_id = request.POST['client_id']
        #client = Client.objects.get(company=company,id=client_id)
        transfer_map = ClientTransferMap.objects.get(company=company,id=experience_id)
        transfer_map.experience = experience
        transfer_map.save()
    return HttpResponse("Changed Status")
