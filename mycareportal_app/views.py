from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from mycareportal_app.forms import *
from mycareportal_app.models import *
#from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages
from django.db import IntegrityError

import datetime
import pytz
import django.utils.timezone as timezone

# Create your views here.

@login_required
def home(request):
    context = {}
    current_company = request.user.company
    user = request.user
    user_roles = UserRoles.objects.filter(company=current_company, user=user)
    user_roles = [x.role for x in user_roles]
    if "CAREMANAGER" in user_roles:
        return redirect('dashboard')
    elif "CAREGIVER" in user_roles:
        if "tablet_id" in request.session:
            #if "current_time_sheet" not in request.session:
            set_caregiver_time_sheet_session(request)
        return redirect('caregiver_dashboard')
    elif "FAMILYUSER" in user_roles:
        return redirect('family_dashboard')
    else:
        return redirect('login')

def login(request):
    return render(request, 'production/wecare_login.html')

@login_required
def logout_view(request):
    current_company = request.user.company
    user = request.user
    user_roles = UserRoles.objects.filter(company=current_company, user=user)
    user_roles = [x.role for x in user_roles]
    if "CAREGIVER" in user_roles:
        if "tablet_id" in request.session:
            if "current_time_sheet" in request.session:
                end_caregiver_time_sheet_session(request)
    logout(request)
    return redirect('login')

@transaction.atomic
def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ManagerRegistrationForm();
        return render(request, 'production/wecare_register.html', context)
    elif request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        context['form'] = form
        if not form.is_valid():
            return render(request, 'production/wecare_register.html', context)
        company_name = form.cleaned_data['company_name']
        contact_number = form.cleaned_data['contact_number']
        address = form.cleaned_data['address']
        city = form.cleaned_data['city']
        state = form.cleaned_data['state']
        zip_code = form.cleaned_data['zip_code']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['email']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        exception_flag = False
        #Create company object and save
        try:
            new_company = Company(company_name=company_name,
                                        contact_number=contact_number,
                                        address=address,
                                        city=city,
                                        state=state,
                                        zip_code=zip_code)
            new_company.save()
        except IntegrityError as e:
            exception_flag = True
            messages.error(request, "Company has already been registered. Please enter a new company name.")
        if not exception_flag:
            try:
                #Create care manager user auth object and save
                new_user = User.objects.create_user(username=username,
                                                    email=email,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    password=password,
                                                    company=new_company)
                new_user.save()
            except IntegrityError as e:
                exception_flag = True
                messages.error(request, "User has already been registered. Please enter a new email address.")
        if not exception_flag:
            try:
                #Create care manager object and save
                new_care_manager = CareManager(user=new_user,
                                               company=new_company,
                                               email_address=email)
                new_care_manager.save()
            except IntegrityError as e:
                exception_flag = True
                messages.error(request, "User has already been registered. Please enter a new email address.")
        if not exception_flag:
            #Add new user to UserRoles with CAREMANAGER role
            new_role = UserRoles(company=new_company,
                                    user=new_user,
                                    role='CAREMANAGER')
            new_role.save()
            #Authenticate new user and log in
            new_user = authenticate(username=username,
                                    password=password)
            auth_login(request, new_user)
            return redirect('home')
    return render(request, 'production/wecare_register.html', context)

@login_required
def dashboard(request):
    context = {}
    current_company = request.user.company
    total_clients = Client.objects.filter(company=current_company).count()
    total_caregivers = Caregiver.objects.filter(company=current_company).count()
    total_family_users = FamilyContact.objects.filter(company=current_company).count()
    total_providers = Provider.objects.filter(company=current_company).count()
    total_care_managers = CareManager.objects.filter(company=current_company).count()
    registered_tablets = ClientTabletRegister.objects.filter(company=current_company).count()
    default_tasks = DefaultTasks.objects.count()
    custom_tasks = Tasks.objects.filter(company=current_company).count()
    total_scheduled_tasks = TaskSchedule.objects.filter(company=current_company).count()
    total_pending_tasks = TaskSchedule.objects.filter(company=current_company,pending=True).count()
    total_in_progress_tasks = TaskSchedule.objects.filter(company=current_company,in_progress=True).count()
    total_completed_tasks = TaskSchedule.objects.filter(company=current_company,complete=True).count()
    total_cancelled_tass = TaskSchedule.objects.filter(company=current_company,cancelled=True).count()
    company_details = {
        'company_name' : current_company.company_name,
        'contact_number' : current_company.contact_number,
        'address' : "{0}, {1} {2}, {3}".format(current_company.address,
                                            current_company.city,
                                            current_company.state,
                                            current_company.zip_code)
    }
    #Add totals to context
    context['total_clients'] = total_clients
    context['total_caregivers'] = total_caregivers
    context['total_family_users'] = total_family_users
    context['total_providers'] = total_providers
    context['total_care_managers'] = total_care_managers
    context['registered_tablets'] = registered_tablets
    context['default_tasks'] = default_tasks
    context['custom_tasks'] = custom_tasks
    context['total_scheduled_tasks'] = total_scheduled_tasks
    context['total_pending_tasks'] = total_pending_tasks
    context['total_in_progress_tasks'] = total_in_progress_tasks
    context['total_completed_tasks'] = total_completed_tasks
    context['total_cancelled_tass'] = total_cancelled_tass
    #Add company details to context
    context['company_details'] = company_details
    return render(request, 'production/admin_dashboard.html', context)

class AddCareManager(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        context['add_care_manager_form'] = CareManagerRegistrationForm()
        return render(request, 'production/add_care_manager.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        add_care_manager_form = CareManagerRegistrationForm(request.POST)
        if add_care_manager_form.is_valid():
            try:
                first_name = add_care_manager_form.cleaned_data['first_name']
                last_name = add_care_manager_form.cleaned_data['last_name']
                email = add_care_manager_form.cleaned_data['email']
                password = add_care_manager_form.cleaned_data['password']
                can_add = add_care_manager_form.cleaned_data['can_add']
                new_user = User.objects.create_user(username=email,
                                                    email=email,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    password=password,
                                                    company=current_company)
                new_user.save()
                #Create care manager object and save
                new_care_manager = CareManager(user=new_user,
                                               company=current_company,
                                               email_address=email,
                                               can_add=can_add)
                new_care_manager.save()
                #Add new user to UserRoles with CAREMANAGER role
                new_role = UserRoles(company=current_company,
                                        user=new_user,
                                        role='CAREMANAGER')
                new_role.save()
                messages.success(request, "Care Manager {0} {1} successfully Added!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Care Manager already exists. Please enter a different Care Manager")
        context['add_care_manager_form'] = CareManagerRegistrationForm();
        return render(request, 'production/add_care_manager.html', context)

class ViewActiveCaregivers(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        active_caregiver_timesheets = CaregiverTimeSheet.objects.filter(company=current_company, is_active=True)
        context['active_caregiver_timesheets'] = self.construct_timesheet_rows(active_caregiver_timesheets)
        return render(request, 'production/view_active_caregivers.html', context)

    def construct_timesheet_rows(self, active_caregiver_timesheets):
        active_caregiver_timesheets = list(map(lambda x: {
                                                        "caregiver_name": "{0} {1}".format(x.caregiver.first_name,x.caregiver.last_name),
                                                        "client_name": "{0} {1}".format(x.client.first_name,x.client.last_name),
                                                        "clock_in_time": (x.clock_in_timestamp.astimezone(pytz.timezone(x.client_timezone))).replace(tzinfo=None),
                                                        "time_worked": timezone.now() - x.clock_in_timestamp
                                                    }, active_caregiver_timesheets))
        return active_caregiver_timesheets

class ViewDailyIncidents(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        clients = Client.objects.filter(company=current_company).order_by('last_name')
        today_incidents = []
        for client in clients:
            client_timezone = pytz.timezone(client.time_zone)
            current_date = (timezone.now().astimezone(client_timezone)).date()
            client_incidents = list(IncidentReport.objects.filter(company=current_company,client=client, incident_timestamp__date = current_date))
            for client_incident in client_incidents:
                client_incident.incident_timestamp = (client_incident.incident_timestamp.astimezone(client_timezone)).replace(tzinfo=None)
            if(len(client_incidents)!=0):
                today_incidents += client_incidents
        context['today_incidents'] = today_incidents
        return render(request, 'production/view_daily_incidents.html', context)

class EditCompany(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        company_edit_form = CompanyEditForm(initial=
        {
            'company_name': current_company.company_name,
            'account_number': current_company.account_number,
            'contact_number': current_company.contact_number,
            'address': current_company.address,
            'city': current_company.city,
            'state': current_company.state,
            'zip_code': current_company.zip_code
        })
        context['company_edit_form'] = company_edit_form
        context['current_company'] = current_company
        return render(request, 'production/edit_company.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        company_edit_form = CompanyEditForm(request.POST)
        if company_edit_form.is_valid():
            try:
                current_company.company_name = company_edit_form.cleaned_data['company_name']
                current_company.account_number = company_edit_form.cleaned_data['account_number']
                current_company.contact_number = company_edit_form.cleaned_data['contact_number']
                current_company.address = company_edit_form.cleaned_data['address']
                current_company.city = company_edit_form.cleaned_data['city']
                current_company.state = company_edit_form.cleaned_data['state']
                current_company.zip_code = company_edit_form.cleaned_data['zip_code']
                current_company.save()
                messages.success(request, "Company details successfully edited")
            except IntegrityError as e:
                messages.error(request, "Company with entered name already exists. Please enter a different name.")
        else:
            messages.error(request, "Error editing company details")
        return redirect('edit_company')

def set_tablet_id_session(request):
    if request.method == 'GET':
        tablet_id = request.GET.get('tablet_id')
        request.session["tablet_id"] = tablet_id
        return HttpResponse("Set Tablet ID")

@login_required
def set_caregiver_time_sheet_session(request):
    print("BEGAN SESSION")
    current_company = request.user.company
    current_caregiver = Caregiver.objects.get(company=current_company, user=request.user)
    tablet_id = request.session["tablet_id"]
    tablet_client = ClientTabletRegister.objects.get(company=request.user.company,device_id=tablet_id)
    client_data = tablet_client.client

    #client_timezone = pytz.timezone(client_data.time_zone)
    #current_date = datetime.date.today()
    #current_date = (timezone.now().astimezone(client_timezone)).date()

    current_time_sheet = CaregiverTimeSheet(company = current_company,
                                            caregiver = current_caregiver,
                                            client = client_data,
                                            clock_in_timestamp = timezone.now(),
                                            client_timezone = client_data.time_zone,
                                            is_active = True)
    current_time_sheet.save()
    request.session['current_time_sheet'] = current_time_sheet.id

@login_required
def end_caregiver_time_sheet_session(request):
    print("ENDED SESSION")
    current_time_sheet = CaregiverTimeSheet.objects.get(company=request.user.company, id=request.session['current_time_sheet'])
    current_time_sheet.clock_out_timestamp = timezone.now()
    current_time_sheet.is_active = False
    time_worked = current_time_sheet.clock_out_timestamp - current_time_sheet.clock_in_timestamp
    print(time_worked)
    current_time_sheet.time_worked = time_worked
    current_time_sheet.save()
    print(current_time_sheet.time_worked)
    del request.session['current_time_sheet']
    request.session.modified = True
