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
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.contrib import messages
from django.db import IntegrityError

from django.contrib.sites.shortcuts import get_current_site

import datetime
import pytz
import django.utils.timezone as timezone

from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from mycareportal_app.email.care_manager.care_manager_email_processor import CareManagerEmailProcessor
from mycareportal_app.email.caregiver.caregiver_email_processor import CaregiverEmailProcessor
from mycareportal_app.email.user.user_email_processor import UserEmailProcessor
from mycareportal_app.email.admin.admin_email_processor import AdminEmailProcessor

from django.db.models.signals import pre_save
from django.dispatch import receiver

from mycareportal_app.common import error_messaging as error_messaging

from mycareportal_app.common.core.event import Event
import uuid
from mycareportal_app.client_forms import *
from mycareportal_app.family_forms import *
from mycareportal_app.caregiver_forms import *
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from random import randint
import requests
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from decimal import Decimal
from django.core.files import File
import xlwt


# Create your views here.


# from django.http import FileResponse
#@receiver(pre_save, sender=User)
#def user_sign_up_(sender, instance, **kwargs):
#    if instance._state.adding:
#        instance.is_active = False

@login_required
def home(request):
    context = {}
    current_company = request.user.company
    user = request.user
    save_caregiver_location(request)
    save_fcm_token(request)
    user_roles = UserRoles.objects.filter(company=current_company, user=user)
    user_roles = [x.role for x in user_roles]
    if current_company.is_on_free_trial:
        current = datetime.datetime.now()
        current = current.replace(tzinfo=None)
        company_created = current_company.created.replace(tzinfo=None)
        free_trial_days = (current - company_created).days
        messages.info(request, "Currently on day {0} of free trial".format(free_trial_days))
    if "tablet_id" in request.session and not current_company.requires_tablet:
        request.session.pop("tablet_id")
    if "CAREMANAGER" in user_roles:
        if "CAREGIVER" in user_roles and "tablet_id" in request.session:
            if ClientTabletRegister.objects.filter(company=request.user.company,device_id=request.session["tablet_id"]).exists():
                #if "current_time_sheet" not in request.session:
                set_caregiver_time_sheet_session(request)
            else:
                messages.error(request, "Tablet is not registered. Please register the tablet to a client.")

        if current_company.default_dashboard == current_company.admin_dashboard:
            return redirect('dashboard')
        elif current_company.default_dashboard == current_company.client_task_dashboard:
            return redirect('client_task_dashboard')
        elif current_company.default_dashboard == current_company.caregiver_schedule_dashboard:
            return redirect('caregiver_schedule_dashboard')
        elif current_company.default_dashboard == current_company.management_dashboard:
            return redirect('management_dashboard')
    elif "CAREGIVER" in user_roles:
        if "tablet_id" in request.session:
            if ClientTabletRegister.objects.filter(company=request.user.company,device_id=request.session["tablet_id"]).exists():
                #if "current_time_sheet" not in request.session:
                set_caregiver_time_sheet_session(request)
            else:
                messages.error(request, "Tablet is not registered. Please register the tablet to a client.")
                return redirect('login')

        return redirect('caregiver_dashboard')
    elif "FAMILYUSER" in user_roles:
        return redirect('family_dashboard')
    elif "PROVIDERUSER" in user_roles:
        return redirect('provider_dashboard')
    elif "HOMEMODUSER" in user_roles:
        return redirect('contractor_dashboard')
    elif "MOVEMANAGER" in user_roles:
        return redirect('move_manager_dashboard')
    else:
        return redirect('login')

def login(request):
    return render(request, 'production/wecare_login.html')

def handler500(request):
    return render(request, 'production/500.html', status=500)

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

@login_required
def caregiver_logout_view(request):
    current_company = request.user.company
    user = request.user
    return redirect('logout')


def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] = ManagerRegistrationForm();
        context['all_timezones'] = pytz.all_timezones
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
        time_zone = form.cleaned_data['time_zone']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['email']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        activation_code = form.cleaned_data['activation_code']
        other_state_name = form.cleaned_data['other_state_name']
        exception_flag = False
        #Check Activation code
        if ActivationCode.objects.filter(activation_code = activation_code, activated=False).exists():
            activation_flag = True
        else:
            activation_flag = False

        #if not activation_flag:
            #messages.error(request, "Invalid Activation Code. Please enter a valid activation code.")
            #return render(request, 'production/wecare_register.html', context)

        #Create company object and save
        with transaction.atomic():
            if activation_flag:
                activation_code_data = ActivationCode.objects.get(activation_code=activation_code)
                activation_code_data.activated = True
                activation_code_data.save()
            try:
                if state == "Other":
                    state = other_state_name

                new_company = Company(company_name=company_name,
                                            contact_number=contact_number,
                                            address=address,
                                            city=city,
                                            state=state,
                                            zip_code=zip_code,
                                            time_zone=time_zone)
                new_company.save()
                if activation_flag:
                    new_company.activated = True
                    activation_code_data = ActivationCode.objects.get(activation_code=activation_code)
                    new_company.activation_code = activation_code_data
                    new_company.is_on_free_trial = False
                    new_company.save()
                else:
                    new_company.is_on_free_trial = True
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
        if not exception_flag:
            #Send verification email
            new_user = User.objects.get(id=new_user.id)
            new_user.is_active = False
            new_user.save()
            current_site = get_current_site(request)
            email_manager = CareManagerEmailProcessor()
            email_manager.send_verification_email(
            new_user, current_site.domain
            )
            #Send email to me and Linda
            email_manager = AdminEmailProcessor()
            email_manager.send_company_sign_up_email(
                new_user, current_site.domain
            )
            #Authenticate new user and log in
            new_user = authenticate(username=username,
                                    password=password)
            #auth_login(request, new_user)
            messages.info(request, "Company {0} and Care Manager {1} {2} successfully Added! Please refer to verification email sent to {3} to complete registration".format(company_name,first_name,last_name,email))
            return redirect('home')
    return render(request, 'production/wecare_register.html', context)

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.account_activated = True
        user.save()
        auth_login(request, user)
        # return redirect('home')
        # Generate one time message for account activation
        messages.success(request, "Account successfully activated")
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')

class PasswordActivate(View):

    def get(self, request):
        context = {}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            return render(request, "production/wecare_pwd_reset.html", context)

def pwd_activate(request, uidb64, token):
    if request.method == "GET":
        context = {}
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            context['user'] = user
            context['uidb64'] = uidb64
            context['token'] = token
            context['form'] = PasswordResetForm()
            return render(request, "production/wecare_pwd_reset.html", context)
        else:
            return HttpResponse("Activation link is invalid")

def reset_password(request):
    if request.method == "POST":
        context = {}
        form = PasswordResetForm(request.POST)
        uidb64 = request.POST.get("uidb64")
        token = request.POST.get("token")
        if form.is_valid():
            password = form.cleaned_data["password"]
            user_id = form.cleaned_data["user_id"]
            uidb64 = form.cleaned_data["uidb64"]
            token = form.cleaned_data["token"]
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.is_active = True
            user.account_activated = True
            user.save()
            messages.success(request, "Password reset. You can now log in.")
        else:
            form_errors = form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
            return redirect("pwd_activate", uidb64=uidb64, token=token)
        return redirect("login")


#Capturing user Latitude and longitude

def set_user_lat_long_session(request):
    if request.method == 'GET':
        user_lat = request.GET.get('user_lat')
        user_long = request.GET.get('user_long')
        request.session["user_lat"] = user_lat
        request.session["user_long"] = user_long
        return HttpResponse("Set Location")

def save_caregiver_location(request):
    if request.session.get("user_long") and request.session.get("user_lat"):
        user_location = UserLocation(company = request.user.company,
                                     user = request.user,
                                     user_long = request.session["user_long"],
                                     user_lat = request.session["user_lat"],
                                     created = datetime.datetime.now())
        user_location.save()

#This method will work perfectly while working with android.
def save_fcm_token(request):
    print("******************* :", request.session.get("fcm_token"))
    if request.session.get("fcm_token"):
        token = UserFcmTokenMap.get_or_create(request.user, request.session.get('fcm_token'))
        if token is not None:
            token.fcm_token =  request.session.get('fcm_token')
            token.save()

#For Setting FCM token in session
#While updating token from website
#it is happening after getting logged in becasue of that
#save_fcm_token method called before set_user_fcm_token and due to
#which it get blank token.
#In this method, I have checked the user in request and added the token.
def set_user_fcm_token(request):
    if request.method == 'GET':
        if request.user is not None:
            token = UserFcmTokenMap.get_or_create(request.user, request.GET.get('fcm_token'))
            if token is not None:
                token.fcm_token =  request.GET.get('fcm_token')
                token.save()

        fcm_token = request.GET.get('fcm_token')
        request.session["fcm_token"] = fcm_token
        return HttpResponse("Set FCM Token")


class ForgotPassword(View):

    def get(self, request):
        context = {}
        context['password_form'] = ForgotPasswordForm()
        return render(request, 'production/wecare_pwd_forgot.html', context)

    @transaction.atomic
    def post(self, request):
        context = {}
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            #Send reset email
            try:
                email = form.cleaned_data['email']
                user = User.objects.get(email=email)
                user.account_activated = False
                user.save()
                current_site = get_current_site(request)
                email_manager = UserEmailProcessor()
                email_manager.pwd_reset_email(
                user, current_site.domain
                )
                messages.success(request, "Sent password reset email to {0}".format(email))
            except:
                messages.error(request, "Error sending password reset email")
        else:
            messages.error(request, "Error sending password reset email")
        return redirect('login')


def pwd_activate_2(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.account_activated = True
        user.save()
        auth_login(request, user)
        # return redirect('home')
        # Generate one time message for account activation
        messages.success(request, "Account successfully activated")
        return redirect('home')
    else:
        return HttpResponse('Activation link is invalid!')

@login_required
def dashboard(request):
    context = {}
    current_company = request.user.company

    if current_company.default_dashboard == current_company.client_task_dashboard:
        return redirect('client_task_dashboard')
    elif current_company.default_dashboard == current_company.caregiver_schedule_dashboard:
        return redirect('caregiver_schedule_dashboard')

    company_timezone = pytz.timezone(current_company.time_zone)
    current_date = (timezone.now().astimezone(company_timezone)).date()
    total_clients = Client.objects.filter(company=current_company).count()
    total_caregivers = Caregiver.objects.filter(company=current_company).count()
    total_family_users = FamilyContact.objects.filter(company=current_company).count()
    total_providers = Provider.objects.filter(company=current_company).count()
    total_care_managers = CareManager.objects.filter(company=current_company).count()
    registered_tablets = ClientTabletRegister.objects.filter(company=current_company).count()
    default_tasks = DefaultTasks.objects.count()
    custom_tasks = Tasks.objects.filter(company=current_company).count()
    total_scheduled_tasks = TaskSchedule.objects.filter(company=current_company,date=current_date).count()
    total_pending_tasks = TaskSchedule.objects.filter(company=current_company,date=current_date,pending=True).count()
    total_in_progress_tasks = TaskSchedule.objects.filter(company=current_company,date=current_date,in_progress=True).count()
    total_completed_tasks = TaskSchedule.objects.filter(company=current_company,date=current_date,complete=True).count()
    total_cancelled_tass = TaskSchedule.objects.filter(company=current_company,date=current_date,cancelled=True).count()
    total_client_at_high_risk = NotifyClientVitalTask.objects.filter(company=current_company).count()
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
    context['total_cancelled_tasks'] = total_cancelled_tass
    context['total_client_at_high_risk'] = total_client_at_high_risk
    #Add company details to context
    context['company_details'] = company_details
    context['company_created_date'] = current_company.created
    days_since_company_created = (timezone.now() - current_company.created).days
    context['days_since_company_created'] = days_since_company_created
    context['current_date'] = '{0}-{1}-{2}'.format(current_date.year,current_date.strftime('%m'),current_date.strftime('%d'))
    print(context['current_date'])
    client_notify = NotifyClientVitalTask.objects.filter(company = current_company,is_active = True)
    context['client_notify'] = client_notify
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
                can_add = add_care_manager_form.cleaned_data['can_add']
                new_user = User.objects.create_user(username=email,
                                                    email=email,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    company=current_company)
                new_user.is_active = False
                new_user.set_unusable_password()
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
                #Send verification email
                current_site = get_current_site(request)
                email_manager = CareManagerEmailProcessor()
                email_manager.new_send_verification_email(
                new_user, current_site.domain
                )
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
        context['close_caregiver_session_form'] = CloseCaregiverSessionForm()
        return render(request, 'production/view_active_caregivers.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        close_caregiver_session_form = CloseCaregiverSessionForm(request.POST)
        if close_caregiver_session_form.is_valid():
            caregiver_session_id = close_caregiver_session_form.cleaned_data['caregiver_session_id']
            clock_out_date = close_caregiver_session_form.cleaned_data['clock_out_date']
            end_hour = close_caregiver_session_form.cleaned_data['end_hour']
            end_minute = close_caregiver_session_form.cleaned_data['end_minute']
            reason = close_caregiver_session_form.cleaned_data['reason']
            self.close_caregiver_time_sheet_session(current_company, caregiver_session_id, clock_out_date, end_hour, end_minute, reason)
        return redirect('view_active_caregivers')

    def construct_timesheet_rows(self, active_caregiver_timesheets):
        active_caregiver_timesheets = list(map(lambda x: {
                                                        "caregiver_name": "{0} {1}".format(x.caregiver.first_name,x.caregiver.last_name),
                                                        "client_name": "{0} {1}".format(x.client.first_name,x.client.last_name),
                                                        "clock_in_time": (x.clock_in_timestamp.astimezone(pytz.timezone(x.client_timezone))).replace(tzinfo=None),
                                                        "time_worked": str(timezone.now() - x.clock_in_timestamp).split(".")[0],
                                                        "id": x.id
                                                    }, active_caregiver_timesheets))
        return active_caregiver_timesheets

    def close_caregiver_time_sheet_session(self, company, caregiver_session_id, clock_out_date, end_hour, end_minute, reason):
        current_time_sheet = CaregiverTimeSheet.objects.get(company=company, id=caregiver_session_id)
        if (clock_out_date and end_hour and end_minute):
            clock_out_time = datetime.time(int(end_hour), int(end_minute))
            clock_out_timestamp = datetime.datetime.combine(clock_out_date, clock_out_time)
            clock_out_timestamp_local = clock_out_timestamp.astimezone(pytz.timezone(current_time_sheet.client_timezone))
            current_time_sheet.adjusted_clock_out_timestamp = clock_out_timestamp.astimezone(current_time_sheet.clock_in_timestamp.tzinfo)
            utc_offset = clock_out_timestamp_local.utcoffset()
            current_time_sheet.adjusted_clock_out_timestamp -= utc_offset
            adjusted_time_worked = current_time_sheet.adjusted_clock_out_timestamp - current_time_sheet.clock_in_timestamp
            current_time_sheet.adjusted_time_worked = adjusted_time_worked
        current_time_sheet.clock_out_timestamp = timezone.now()
        current_time_sheet.is_active = False
        time_worked = current_time_sheet.clock_out_timestamp - current_time_sheet.clock_in_timestamp
        current_time_sheet.time_worked = time_worked
        current_time_sheet.manual_clock_out = True
        if reason:
            current_time_sheet.reason = reason
        current_time_sheet.save()
        print(current_time_sheet.time_worked)

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
        is_parent_flag =True
        current_company = request.user.company
        company_edit_form = CompanyEditForm(initial=
        {
            'company_name': current_company.company_name,
            'account_number': current_company.account_number,
            'contact_number': current_company.contact_number,
            'address': current_company.address,
            'city': current_company.city,
            'state': current_company.state,
            'zip_code': current_company.zip_code,
            'time_zone': current_company.time_zone,
            'default_dashboard': current_company.default_dashboard,
            'tax_rate': current_company.tax_rate,
            'logo': current_company.logo,
            'attorney_email': current_company.attorney_email,
            'is_parent':current_company.is_parent,
            'mileage_rate': current_company.mileage_rate
        })
        caregiver = Caregiver.objects.filter(company = current_company).count()
        client = Client.objects.filter(company = current_company).count()
        if caregiver > 0 and  client > 0 :
            is_parent_flag = False

        context['company_edit_form'] = company_edit_form
        
        context['current_company'] = current_company
        context['all_timezones'] = pytz.all_timezones
        context['is_parent_flag'] = is_parent_flag
        return render(request, 'production/edit_company.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        company_edit_form = CompanyEditForm(request.POST, request.FILES)
        if company_edit_form.is_valid():
            try:
                current_company.company_name = company_edit_form.cleaned_data['company_name']
                current_company.account_number = company_edit_form.cleaned_data['account_number']
                current_company.contact_number = company_edit_form.cleaned_data['contact_number']
                current_company.address = company_edit_form.cleaned_data['address']
                current_company.city = company_edit_form.cleaned_data['city']
                current_company.state = company_edit_form.cleaned_data['state']
                current_company.zip_code = company_edit_form.cleaned_data['zip_code']
                current_company.time_zone = company_edit_form.cleaned_data['time_zone']
                current_company.default_dashboard = company_edit_form.cleaned_data['default_dashboard']
                current_company.tax_rate = company_edit_form.cleaned_data['tax_rate']
                current_company.logo = company_edit_form.cleaned_data['logo']
                current_company.attorney_email = company_edit_form.cleaned_data['attorney_email']
                current_company.is_parent = company_edit_form.cleaned_data['is_parent']
                current_company.mileage_rate = company_edit_form.cleaned_data['mileage_rate']
                other_state_name = company_edit_form.cleaned_data['other_state_name']
                if current_company.state == "Other":
                    current_company.state = other_state_name
                

                current_company.save()
                #send_mail('Test sendgrid', 'Test message', 'info@wecareportal.com', ['dhruv.ranjan@gmail.com'], fail_silently=False)
                messages.success(request, "Company details successfully edited")
            except IntegrityError as e:
                messages.error(request, "Company with entered name or account number already exists. Please enter a different name or account number.")
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
    # Send clock in email to care managers and family members of client
    care_managers = CareManager.objects.filter(company=current_company)
    family_members = client_data.family_contacts.filter(is_active=True)
    # get clock in Timestamp
    client_time_zone = pytz.timezone(client_data.time_zone)
    clock_in_timestamp = timezone.now().astimezone(client_time_zone).replace(tzinfo=None)
    email_manager = CaregiverEmailProcessor()
    email_manager.send_clock_in_email(
    client_data, current_caregiver, care_managers, family_members, clock_in_timestamp
    )
    request.session['current_time_sheet'] = current_time_sheet.id

@login_required
def end_caregiver_time_sheet_session(request):
    current_time_sheet = CaregiverTimeSheet.objects.get(company=request.user.company, id=request.session['current_time_sheet'])
    current_time_sheet.clock_out_timestamp = timezone.now()
    current_time_sheet.is_active = False
    client = current_time_sheet.client
    current_caregiver = current_time_sheet.caregiver
    time_worked = current_time_sheet.clock_out_timestamp - current_time_sheet.clock_in_timestamp
    current_time_sheet.time_worked = time_worked
    current_time_sheet.save()
    # Send clock out email to care managers and family members of client
    care_managers = CareManager.objects.filter(company=request.user.company)
    family_members = client.family_contacts.filter(is_active=True)
    # get clock out Timestamp
    print(client.time_zone)
    client_time_zone = pytz.timezone(client.time_zone)
    clock_out_timestamp = timezone.now().astimezone(client_time_zone).replace(tzinfo=None)
    print(clock_out_timestamp)
    email_manager = CaregiverEmailProcessor()
    email_manager.send_clock_out_email(
    client, current_caregiver, care_managers, family_members, clock_out_timestamp
    )
    del request.session['current_time_sheet']
    request.session.modified = True

@login_required
def date_filter_dashboard(request):
    dashboard_task_data = {}
    current_company = request.user.company
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    #company_time_zone = current_company.time_zone
    #company_time_zone = pytz.timezone(company_time_zone)
    #current_date = (timezone.now().astimezone(client_timezone)).date()
    #timezone.activate(client_timezone)
    #default_tasks = DefaultTasks.objects.count()
    #custom_tasks = Tasks.objects.filter(company=current_company).count()
    print("start_date :",start_date)
    total_scheduled_tasks = TaskSchedule.objects.filter(company=current_company,date__range=[start_date,end_date]).count()
    total_pending_tasks = TaskSchedule.objects.filter(company=current_company,pending=True,date__range=[start_date,end_date]).count()
    total_in_progress_tasks = TaskSchedule.objects.filter(company=current_company,in_progress=True,date__range=[start_date,end_date]).count()
    total_completed_tasks = TaskSchedule.objects.filter(company=current_company,complete=True,date__range=[start_date,end_date]).count()
    total_cancelled_tasks = TaskSchedule.objects.filter(company=current_company,cancelled=True,date__range=[start_date,end_date]).count()

    #context['default_tasks'] = default_tasks
    #context['custom_tasks'] = custom_tasks
    dashboard_task_data['total_scheduled_tasks'] = total_scheduled_tasks
    dashboard_task_data['total_pending_tasks'] = total_pending_tasks
    dashboard_task_data['total_in_progress_tasks'] = total_in_progress_tasks
    dashboard_task_data['total_completed_tasks'] = total_completed_tasks
    dashboard_task_data['total_cancelled_tasks'] = total_cancelled_tasks
    return HttpResponse(json.dumps(dashboard_task_data),content_type="application/json")

class ViewEventLog(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        company = request.user.company
        company_timezone = pytz.timezone(company.time_zone)
        current_timestamp = (timezone.now().astimezone(company_timezone))
        current_date = current_timestamp.date()
        caregivers = Caregiver.objects.filter(company=company)
        active_caregivers = list(map(lambda x: x.caregiver, CaregiverTimeSheet.objects.filter(company=company,is_active=True)))
        caregiver_schedule = CaregiverSchedule.objects.filter(company=company,date=current_date)
        (late_caregivers, not_clocked_out_caregivers) = self.get_late_caregivers(company, caregiver_schedule, active_caregivers, caregivers)
        #not_clocked_out_caregivers = self.get_not_clocked_out(company, caregiver_schedule, active_caregivers, caregivers)


        events = late_caregivers + not_clocked_out_caregivers
        events.sort(key=lambda x: x.time, reverse=True)
        context['events'] = events
        return render(request, "production/event_log.html", context)

    def get_late_caregivers(self, company, caregiver_schedule, active_caregivers, caregivers):

        late_caregivers = []
        not_clocked_out_caregivers = []

        for schedule in caregiver_schedule:
            client = schedule.client

            client_timezone = pytz.timezone(client.time_zone)
            #current_date = datetime.date.today()
            current_timestamp = (timezone.now().astimezone(client_timezone))
            current_date = current_timestamp.date()
            current_time = current_timestamp.time()

            clock_in_date = schedule.date
            clock_in_time = schedule.start_time
            clock_out_time = schedule.end_time
            if schedule.caregiver in active_caregivers:
                late_time = clock_out_time.replace(minute=clock_out_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    event_name = "Late Clock Out"
                    description = '''Caregiver {0} {1} has not clocked out from shift at
                                    client {2} {3}. Expected
                                    clock out was at {4}'''.format(schedule.caregiver.first_name,
                                    schedule.caregiver.last_name,client.first_name,client.last_name,
                                    clock_out_time.strftime("%I:%M %p"))
                    status = "warning"
                    date = clock_in_date
                    time = late_time
                    event = Event(event_name,description,status,date,time)
                    not_clocked_out_caregivers.append(event)
            else:
                late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    event_name = "Late Clock In"
                    description = '''Caregiver {0} {1} has not clocked into shift at
                                    client {2} {3}. Expected
                                    clock in was at {4}'''.format(schedule.caregiver.first_name,
                                    schedule.caregiver.last_name,client.first_name,client.last_name,
                                    clock_in_time.strftime("%I:%M %p"))
                    status = "warning"
                    date = clock_in_date
                    time = late_time
                    event = Event(event_name,description,status,date,time)
                    late_caregivers.append(event)
        '''for caregiver in caregivers:
            if caregiver not in active_caregivers:
                current_schedule = caregiver_schedule.filter(caregiver=caregiver)
                for schedule in current_schedule:
                    client = schedule.client

                    client_timezone = pytz.timezone(client.time_zone)
                    #current_date = datetime.date.today()
                    current_timestamp = (timezone.now().astimezone(client_timezone))
                    current_date = current_timestamp.date()
                    current_time = current_timestamp.time()

                    clock_in_date = schedule.date
                    clock_in_time = schedule.start_time
                    clock_out_time = schedule.end_time
                    late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
                    if clock_in_date == current_date and current_time > late_time:
                        if caregiver not in late_caregivers:
                            late_caregivers.append(caregiver)
            else:
                current_schedule = caregiver_schedule.filter(caregiver=caregiver)
                for schedule in current_schedule:
                    client = schedule.client

                    client_timezone = pytz.timezone(client.time_zone)
                    #current_date = datetime.date.today()
                    current_timestamp = (timezone.now().astimezone(client_timezone))
                    current_date = current_timestamp.date()
                    current_time = current_timestamp.time()

                    clock_in_date = schedule.date
                    clock_in_time = schedule.start_time
                    clock_out_time = schedule.end_time
                    late_time = clock_out_time.replace(minute=clock_out_time.minute+15)
                    if clock_in_date == current_date and current_time > late_time:
                        if caregiver not in not_clocked_out_caregivers:
                            not_clocked_out_caregivers.append(caregiver)'''

        return (late_caregivers, not_clocked_out_caregivers)

class ChooseContractorForTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = HomeModificationTask.objects.get(company=current_company, uid=task_id)
        all_home_mod_managers = HomeModificationUser.objects.filter(company=current_company).order_by('last_name')
        context["assign_contractor_form"] = AssignContractorForm()
        context['all_home_mod_managers'] = all_home_mod_managers
        context['task_id'] = task_id
        context['task'] = task
        return render(request, "production/contractor_tables.html", context)

    def post(self, request, *args, **kwargs):

        context = {}
        current_company = request.user.company
        # task_id = self.kwargs['task_id']
        # contractor_id = self.kwargs['contractor_id']
        assign_contractor_form = AssignContractorForm(request.POST)
        if assign_contractor_form.is_valid():
            contractor_email = assign_contractor_form.cleaned_data['contractor_email']
            taskuid = assign_contractor_form.cleaned_data['taskuid']
            is_unassign = assign_contractor_form.cleaned_data['is_unassign']
            task = HomeModificationTask.objects.get(company=current_company, uid=taskuid)
            contractor = HomeModificationUser.objects.get(company=current_company, email_address = contractor_email )
            
            
            if is_unassign == "True":
                task.chosen_contractors.remove(contractor)
                bids = HomeModTaskBid.objects.filter(company=current_company, home_mod_task=task,contractor =contractor)
                bids.delete()
                if ContractorRejectTask.objects.filter(company=current_company,contractor=contractor,home_mod_task= task,status = True).exists():
                    contractor_task = ContractorRejectTask.objects.get(company=current_company, home_mod_task=task,contractor =contractor,status = True)
                    contractor_task.status = False
                    contractor_task.save()

            else:
                task.chosen_contractors.add(contractor)
                
            task.save()
            
        
        # contractor = HomeModificationUser.objects.get(company=current_company, uid=contractor_id)
        # print(task.uid)
        # print(contractor.uid)
        # task.chosen_contractors.add(contractor)
        
        return redirect('choose_contractor', task_id=taskuid)


class HomeDashboard(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        home_mod_categories = AssessmentCategories.objects.all()
        existing_home_mod_tasks = HomeModificationTask.get_unarchived_tasks(current_company)
        existing_move_manage_tasks = MoveManageTask.get_unarchived_tasks(current_company)
        contractor_reject_bidding = ContractorRejectTask.objects.filter(company=current_company,status = True)
        movemanager_reject_bidding = MoveManagerRejectTask.objects.filter(company = current_company, status = True )
        tzname = current_company.time_zone
        timezone.activate(pytz.timezone(tzname))

        context['all_clients'] = all_clients
        context['home_mod_categories'] = home_mod_categories
        context['create_task_form'] = CreateHomeModTaskForm()
        context['existing_home_mod_tasks'] = existing_home_mod_tasks
        context['existing_move_manage_tasks'] = existing_move_manage_tasks
        context['contractor_reject_bidding'] = contractor_reject_bidding
        context['movemanager_reject_bidding'] = movemanager_reject_bidding

        
        return render(request, "production/view_alerts.html", context)

    @transaction.atomic
    def post(self, request):
        context = {}
        current_company = request.user.company
        home_mod_task_form = CreateHomeModTaskForm(request.POST)
        #print(request.POST)
        #print(home_mod_task_form.data['client_uid'])
        #print(home_mod_task_form.data['assessment_category_uid'])
        #print(home_mod_task_form.data['task_name'])
        #print(home_mod_task_form.data['task_description'])
        if home_mod_task_form.is_valid():
            client_uid = home_mod_task_form.cleaned_data['client_uid']
            client = Client.objects.get(company=current_company, uid = client_uid)
            category_uid = home_mod_task_form.cleaned_data['assessment_category_uid']
            home_mod_category = AssessmentCategories.objects.get(uid=category_uid)
            task_name = home_mod_task_form.cleaned_data['task_name']
            task_description = home_mod_task_form.cleaned_data['task_description']
            new_task = HomeModificationTask(company=current_company,
                                            client=client,
                                            assessment_category=home_mod_category,
                                            task_name=task_name,
                                            task_description=task_description)

            new_task.save()
            messages.success(request, "Task Successfully Added")
        else:
            form_errors = home_mod_task_form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
        return redirect('home_dashboard')

class CaregiverScheduleDashboard(LoginRequiredMixin, View):

    def get(self, request):
        company = request.user.company
        context = {}
        # 1. Get all caregiver schedules for current company for the current week
        current_date = datetime.date.today()
        calendar_dates = []

        calendar_dates.append(current_date - datetime.timedelta(1))
        calendar_dates.append(current_date - datetime.timedelta(2))
        calendar_dates.append(current_date - datetime.timedelta(3))

        calendar_dates.append(current_date)

        calendar_dates.append(current_date + datetime.timedelta(1))
        calendar_dates.append(current_date + datetime.timedelta(2))
        calendar_dates.append(current_date + datetime.timedelta(3))

        caregiver_schedules = CaregiverSchedule.objects.filter(company=company,
                                                               date__in=calendar_dates)
        # 2. Get caregiver dashboard schedule object for company/user,
        # or create one if it currently does not exist
        schedule_dashboard_settings = CaregiverScheduleDashboardSettings.get_or_create(company, request.user)
        # 3. Filter caregiver_schedules from 1. using active filters from settings in 2.
        (filtered_schedules, scheduled_schedules,
        in_progress_schedules, completed_schedules,
        missed_schedules, late_schedules, open_schedules) = self.apply_settings_filters(caregiver_schedules,
                                                                                        schedule_dashboard_settings,
                                                                                        self.request.user.company)
        caregivers = Caregiver.objects.filter(company=company)
        form = CaregiverScheduleDashboardSettingsForm(initial=
            {
                "open_filter": schedule_dashboard_settings.open_filter,
                "scheduled_filter": schedule_dashboard_settings.scheduled_filter,
                "in_progress_filter": schedule_dashboard_settings.in_progress_filter,
                "completed_filter": schedule_dashboard_settings.completed_filter,
                "late_filter": schedule_dashboard_settings.late_filter,
                "missed_filter": schedule_dashboard_settings.missed_filter
            }
        )
        # (late_caregivers, not_clocked_out_caregivers) = self.get_caregiver_details(request)
        context['caregivers'] = caregivers
        context['caregiver_schedules'] = self.to_schedule_objects(filtered_schedules)
        #json.dumps(list(filtered_schedules), cls=DjangoJSONEncoder)
        context['scheduled_schedules'] = self.to_schedule_objects(scheduled_schedules)
        context['in_progress_schedules'] = self.to_schedule_objects(in_progress_schedules)
        context['completed_schedules'] = self.to_schedule_objects(completed_schedules)
        context['missed_schedules'] = self.to_schedule_objects(missed_schedules)
        context['late_schedules'] = self.to_schedule_objects(late_schedules)
        context['open_schedules'] = open_schedules
        context['caregiver_filter'] = schedule_dashboard_settings.caregiver_filter.all()
        context['unselected_caregivers'] = list(set(caregivers)-set(schedule_dashboard_settings.caregiver_filter.all()))
        context['dashboard_settings_form'] = form
        return render(request, "production/caregiver_schedule_dashboard.html", context)

    def post(self, request):
        company = request.user.company
        context = {}
        schedule_settings_form = CaregiverScheduleDashboardSettingsForm(request.POST)
        if schedule_settings_form.is_valid():
            schedule_dashboard_settings = CaregiverScheduleDashboardSettings.get_or_create(company, request.user)
            schedule_dashboard_settings.open_filter = schedule_settings_form.cleaned_data['open_filter']
            schedule_dashboard_settings.scheduled_filter = schedule_settings_form.cleaned_data['scheduled_filter']
            schedule_dashboard_settings.in_progress_filter = schedule_settings_form.cleaned_data['in_progress_filter']
            schedule_dashboard_settings.completed_filter = schedule_settings_form.cleaned_data['completed_filter']
            schedule_dashboard_settings.late_filter = schedule_settings_form.cleaned_data['late_filter']
            schedule_dashboard_settings.missed_filter = schedule_settings_form.cleaned_data['missed_filter']
            caregiver_uid_filters = request.POST.getlist('caregiver_filter')
            caregiver_filters = Caregiver.objects.filter(company=company, uid__in=caregiver_uid_filters)
            schedule_dashboard_settings.caregiver_filter = caregiver_filters
            #print(schedule_dashboard_settings.cleaned_data['caregiver_filter'])
            #schedule_dashboard_settings.caregiver_filter = schedule_settings_form.cleaned_data['caregiver_filter']
            schedule_dashboard_settings.save()
            #send_mail('Test sendgrid', 'Test message', 'info@wecareportal.com', ['dhruv.ranjan@gmail.com'], fail_silently=False)
            messages.success(request, "Dashboard settings saved")
        else:
            messages.error(request, "Error saving dashboard settings")
        return redirect('caregiver_schedule_dashboard')


    def to_schedule_objects(self, filtered_schedules):
        schedules = []
        for schedule in filtered_schedules:
            schedule_object = schedule.to_json_schedule()
            schedules.append(schedule_object)
        return schedules

    def apply_settings_filters(self, caregiver_schedules, settings, company):
        filtered_schedules = []
        scheduled_schedules = []
        in_progress_schedules = []
        completed_schedules = []
        missed_schedules = []
        late_schedules = []
        open_schedules = []
        caregiver_filter_active = False
        if settings.caregiver_filter.all().count() > 0:
            caregiver_filter_active = True
        for schedule in caregiver_schedules:
            if caregiver_filter_active and not schedule.caregiver in settings.caregiver_filter.all():
                continue
            if settings.scheduled_filter:
                filtered_schedules.append(schedule)
                scheduled_schedules.append(schedule)
            if settings.in_progress_filter:
                if schedule.is_active():
                    filtered_schedules.append(schedule)
                    in_progress_schedules.append(schedule)
            if settings.completed_filter:
                if schedule.is_complete():
                    filtered_schedules.append(schedule)
                    completed_schedules.append(schedule)
            if settings.missed_filter:
                if schedule.is_missed():
                    filtered_schedules.append(schedule)
                    missed_schedules.append(schedule)
            if settings.late_filter:
                if schedule.is_late():
                    filtered_schedules.append(schedule)
                    late_schedules.append(schedule)
        if settings.open_filter:
            company_timezone = pytz.timezone(company.time_zone)
            current_date = (timezone.now().astimezone(company_timezone)).date()
            if caregiver_filter_active:
                all_caregivers = Caregiver.objects.filter(company=company,
                    id__in=[x.id for x in settings.caregiver_filter.all()])
            else:
                all_caregivers = Caregiver.objects.filter(company=company)
            for caregiver in all_caregivers:
                new_open_schedules = CaregiverSchedule.create_open_schedule_json(company,
                                        caregiver, current_date)
                open_schedules.extend(new_open_schedules)
                #filtered_schedules.extend(new_open_schedules)
        return (filtered_schedules, scheduled_schedules, in_progress_schedules,
                completed_schedules, missed_schedules, late_schedules, open_schedules)

    def get_caregiver_details(self, request):
        company = request.user.company
        company_timezone = pytz.timezone(company.time_zone)
        current_timestamp = (timezone.now().astimezone(company_timezone))
        current_date = current_timestamp.date()
        caregivers = Caregiver.objects.filter(company=company)
        active_caregivers = list(map(lambda x: x.caregiver, CaregiverTimeSheet.objects.filter(company=company,is_active=True)))
        caregiver_schedule = CaregiverSchedule.objects.filter(company=company,date=current_date)
        (late_caregivers, not_clocked_out_caregivers) = self.get_late_caregivers(company, caregiver_schedule, active_caregivers, caregivers)
        #not_clocked_out_caregivers = self.get_not_clocked_out(company, caregiver_schedule, active_caregivers, caregivers)
        return (late_caregivers, not_clocked_out_caregivers)

    def get_late_caregivers(self, company, caregiver_schedule, active_caregivers, caregivers):

        late_caregivers = []
        not_clocked_out_caregivers = []

        for schedule in caregiver_schedule:
            client = schedule.client

            client_timezone = pytz.timezone(client.time_zone)
            #current_date = datetime.date.today()
            current_timestamp = (timezone.now().astimezone(client_timezone))
            current_date = current_timestamp.date()
            current_time = current_timestamp.time()

            clock_in_date = schedule.date
            clock_in_time = schedule.start_time
            clock_out_time = schedule.end_time
            if schedule.caregiver in active_caregivers:
                late_time = clock_out_time.replace(minute=clock_out_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    not_clocked_out_caregivers.append(schedule.caregiver)
            else:
                late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    late_caregivers.append(schedule.caregiver)
        return (late_caregivers, not_clocked_out_caregivers)

class ClientTaskDashboard(LoginRequiredMixin, View):

    def get(self, request):
        company = request.user.company
        context = {}
        client_tasks = TaskSchedule.objects.filter(company=company)
        clients = Client.objects.filter(company=company)
        context['clients'] = clients
        context['client_tasks'] = client_tasks
        return render(request, "production/client_task_dashboard.html", context)

class ChooseClientForInvoice(LoginRequiredMixin, View):

    def get(self, request):
        current_company = request.user.company
        context = {}
        context['client_invoice_form'] = ChooseClientInvoiceForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        invoice_header = InvoiceHeader.objects.filter(company=current_company,submitted = True,cancelled =False)
       
        context['invoice_header'] = invoice_header
        return render(request, "production/choose_client_invoice.html", context)

class Invoice(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        invoice_id = request.GET.get('invoice_id')
        current_company = request.user.company
        context = {}
        current_company = Company.objects.get(company_id = current_company.company_id)
        context['current_company'] = current_company
        current_date = datetime.date.today()
        context['current_date'] =current_date
        if invoice_id:
            submit = True
            context['submit'] = submit
            exits_invoice_header = InvoiceHeader.objects.filter(company = current_company, id = invoice_id,  submitted = True,cancelled =False)
            context['invoice_header_data'] = exits_invoice_header
            invoice_header_data = InvoiceHeader.objects.get(id = exits_invoice_header)
            context['invoice_header_data'] = invoice_header_data
            context['start_date'] = invoice_header_data.start_date
            context['end_date'] = invoice_header_data.end_date
            invoice_line_items = list(InvoiceLineItem.objects.filter(invoice_header = exits_invoice_header,company = current_company).order_by("id"))
            context['invoice_line_items'] = invoice_line_items
            caregiver_schedule_notes = CaregiverSchedule.objects.filter(company = current_company, client= invoice_header_data.client, date__range = (invoice_header_data.start_date, invoice_header_data.end_date))
            context['caregiver_schedule_notes'] = caregiver_schedule_notes
        else:
            submit = False
            context['submit'] = submit
            client_invoice_form = ChooseClientInvoiceForm(request.GET)
            if client_invoice_form.is_valid():
                client_email = client_invoice_form.cleaned_data['client_email']
                client = Client.objects.get(company=current_company, email_address=client_email)
                start_date = client_invoice_form.cleaned_data['start_date']
                end_date = client_invoice_form.cleaned_data['end_date']
                tasks = TaskSchedule.objects.filter(company=current_company,
                                    date__range=(start_date, end_date))
                context['client'] = client
                context['start_date'] = start_date
                context['end_date'] = end_date
                invoice_rate_types = InvoiceRateType.objects.all()
                context['invoice_rate_types'] = invoice_rate_types
                exits_invoice_header = InvoiceHeader.objects.filter(company = current_company,client = client, start_date = start_date,end_date = end_date ,  submitted = True,cancelled =False)
                caregiver_schedule_notes = CaregiverSchedule.objects.filter(company = current_company, client= client, date__range = (start_date, end_date))
                context['caregiver_schedule_notes'] = caregiver_schedule_notes
                if exits_invoice_header:
                    context['invoice_header_data'] = exits_invoice_header
                    invoice_header_data = InvoiceHeader.objects.get(id = exits_invoice_header)
                    context['invoice_header_data'] = invoice_header_data
                    invoice_line_items = list(InvoiceLineItem.objects.filter(invoice_header = invoice_header_data,company = current_company).order_by("id"))
                    context['invoice_line_items'] = invoice_line_items
                    caregiver = client.caregiver.all()
                    context['caregiver'] = caregiver
                    
                    
                else:
                    invoice_header = InvoiceHeader.create_invoice(current_company,client,start_date,end_date)
                    invoice_header_data = InvoiceHeader.objects.get(id =invoice_header.id)
                    context['invoice_header_data'] = invoice_header_data
                    invoice_line_items = list(InvoiceLineItem.objects.filter(invoice_header = invoice_header_data,company = current_company))
                    context['invoice_line_items'] = invoice_line_items
                    task_objects = self.get_line_items(tasks, current_company)
                    total_amt = self.get_total(task_objects)
                    context['task_objects'] = task_objects
                    context['total_amt'] = total_amt
                    
                    caregiver = client.caregiver.all()
                    context['caregiver'] = caregiver
                    invoice_rate_types = InvoiceRateType.objects.all()
                    context['invoice_rate_types'] = invoice_rate_types
                    if current_company.tax_rate:
                        tax_amt= round((invoice_header.total_cost * float(current_company.tax_rate / 100)),2)
                        invoice_header_data.taxes = tax_amt
                        invoice_header_data.total_cost =  invoice_header_data.total_cost +  Decimal.from_float(invoice_header_data.taxes)
                        invoice_header_data.save()
                       
       
        return render(request, "production/invoice.html", context)


       
    
    def get_total(self, task_objects):

        total_amt = 0
        for caregiver, tasks in task_objects.items():
            for task in tasks.items():
                total_amt += task[1]['total']
        return total_amt


    def get_line_items(self, tasks, current_company):
        line_items = []
        task_objects = {}
        # Task Objects should be:
        # 1. TaskSchedule Object
        # 2. Caregiver Objects
        # 3. Hourly rate of caregiver
        # 4. Summed hours for task
        # 5. hourly rate * summed hours
        for task in tasks:
            completed_by = task.completed_by
            if task.start_time != "" and task.end_time != "":
                total_time_hrs = self.getTotalHours(task.start_time, task.end_time)
                if Caregiver.objects.filter(company=current_company, user=completed_by).exists():
                    caregiver = Caregiver.objects.get(company=current_company, user=completed_by)
                    if caregiver in task_objects:
                        if task.activity_task in task_objects[caregiver]:
                            task_object = task_objects[caregiver][task.activity_task]
                            task_object['task_hours'] += total_time_hrs
                            task_object['total'] = task_object['task_hours'] * caregiver.hourly_rate
                            task_objects[caregiver][task.activity_task] = task_object
                        else:
                            task_object = {
                                "task_schedule": task,
                                "caregiver": caregiver,
                                "hourly_rate": caregiver.hourly_rate,
                                "task_hours": total_time_hrs,
                                "description": task.task_header.description,
                                "total": total_time_hrs * caregiver.hourly_rate
                            }
                            task_objects[caregiver][task.activity_task] = task_object
                    else:
                        task_object = {
                            "task_schedule": task,
                            "caregiver": caregiver,
                            "hourly_rate": caregiver.hourly_rate,
                            "task_hours": total_time_hrs,
                            "description": task.task_header.description,
                            "total": total_time_hrs * caregiver.hourly_rate
                        }
                        task_objects[caregiver] = {task.activity_task: task_object}
        return task_objects

    def getTotalHours(self, start_time, end_time):
        start_hour = int(start_time.split(":")[0])
        start_minute = int(start_time.split(":")[1])
        end_hour = int(end_time.split(":")[0])
        end_minute = int(end_time.split(":")[1])
        start_minutes = (start_hour * 60) + start_minute
        end_minutes = (end_hour * 60) + end_minute
        total_time_hrs = abs(end_minutes - start_minutes) / 60
        return total_time_hrs



class ManagerChooseClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_task_form'] = FindClientTaskForm()
        return render(request, 'production/choose_client_manager.html', context)

class ManagerClientDashboard(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        context = {}
        current_company = request.user.company
        find_client_task_form = FindClientTaskForm(request.GET)
        context['all_timezones'] = pytz.all_timezones
        context["update_task_form"] = UpdateAdminManageTaskForm()
        
        if find_client_task_form.is_valid():
            client_email = find_client_task_form.cleaned_data['client_email']
            date_value = find_client_task_form.cleaned_data['date_value']
            client = Client.objects.get(company=current_company, email_address=client_email)
            related_clients = []
            related_clients.append(client)
            related_caregivers = []
            context['client_email'] = client_email
            
            
            for client in related_clients:
                client_caregivers = client.caregiver.all()
                related_caregivers += client_caregivers
            active_caregivers = self.get_active_caregivers(current_company, related_clients, related_caregivers)
            #active_caregivers = CaregiverTimeSheet.objects.filter(company=current_company, client__in=related_clients, caregiver__in=related_caregivers)
            context['active_caregivers'] = active_caregivers
            context['related_caregivers'] = related_caregivers
            #Get displayable family contact data
        

            #Get Tasks for related clients for the current day
            client_tasks = {}
            current_date = datetime.date.today()
            for client_data in related_clients:
                current_client_tasks = self.get_client_tasks(client_data, current_company,date_value)
                #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
                client_tasks[client_data] = list(current_client_tasks)
            context["client_tasks"] = client_tasks
            
       
        return render(request, 'production/manager_client_dashboard.html', context)

    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST, request.FILES)
        if update_task_form.is_valid():
            current_company = request.user.company
            comment = update_task_form.cleaned_data["comment"]
            task_id = update_task_form.cleaned_data["task_id"]
            client_id = update_task_form.cleaned_data["client_id"]
            status = update_task_form.cleaned_data["status"]
            client = Client.objects.get(company=current_company,id=client_id)
            task = TaskSchedule.objects.get(company=current_company,client=client,id=task_id)
            
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
            if status == "complete":
                task.completed_by = self.request.user
                for i in client.caregiver.all():
                    caregiver = CaregiverSchedule.objects.filter(company=current_company,caregiver_id = i.id,date = task.date, start_time = task.start_time, end_time=task.end_time)
                    if caregiver:
                        for i in caregiver:
                            caregiverval = Caregiver.objects.get(company= current_company,id = i.caregiver.id)
                            task.completed_by_caregiver = caregiverval
                task.completed_timestamp = datetime.datetime.now()
            else:
                task.completed_by = None
            task.save()
            date = self.parse_dates(task.date)
            
            self.save_task_comments(request, update_task_form, task, current_company, client, comment)
            messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return HttpResponseRedirect(reverse('manager_client_dashboard') + "?date_value=" + str(task.date) + "&client_email=" + client.email_address)

    def get_active_caregivers(self, current_company, related_clients, related_caregivers):
        client_timezone = pytz.timezone(related_clients[0].time_zone)
        current_date_time = timezone.now().astimezone(client_timezone)
        active_caregivers = CaregiverTimeSheet.objects.filter(company=current_company,
                    client__in=related_clients,
                    caregiver__in=related_caregivers,
                    clock_in_timestamp__year=current_date_time.year,
                    clock_in_timestamp__month=current_date_time.month,
                    clock_in_timestamp__day=current_date_time.day)
        return active_caregivers


    def get_client_tasks(self, client_data, current_company,date_value):
        # client_timezone = pytz.timezone(client_data.time_zone)
        #current_date = datetime.date.today()
        current_date = date_value
        # timezone.activate(client_timezone)
        client_tasks = TaskSchedule.objects.filter(company=current_company,client=client_data,date=current_date)
        client_tasks = list(map(lambda x: (x,
        TaskComment.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created'),
        TaskAttachment.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created'),
        TaskLink.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created')),client_tasks))
        return client_tasks
        
        
    
    def parse_dates(self,task_date):
        # caregiver_birthday = caregiver_birthday.date()
        output_month = task_date.month
        output_day = task_date.day
        output_year = task_date.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

    def save_task_comments(self, request, update_task_form, task, current_company, client, comment):

        #caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        task_comment = TaskComment(company=current_company,
                                    client=client,
                                    user=request.user,
                                    task_schedule=task,
                                    comment=comment)
        if comment != "":
            task_comment.save()

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
def get_caregiver_schedules_with_uids(request):
    if request.method == 'GET':
        context = {}
        company = request.user.company
        caregiver_uids = request.GET.getlist('caregiver_uids[]')
        current_company = request.user.company
        company_timezone = pytz.timezone(current_company.time_zone)
        current_timestamp = (timezone.now().astimezone(company_timezone))
        current_date = current_timestamp.date()
        caregivers = Caregiver.objects.filter(company=company, uid__in=caregiver_uids)
        caregiver_schedules = list(CaregiverSchedule.objects.filter(company=company,
                                caregiver__in=caregivers))
        schedule_objects = []
        (late_caregivers, not_clocked_out_caregivers, active_caregivers) = get_caregiver_details(request)
        for schedule in caregiver_schedules:
            schedule_start_datetime = datetime.datetime.combine(schedule.date, schedule.start_time)
            schedule_end_datetime = datetime.datetime.combine(schedule.date, schedule.end_time)
            schedule_start_datetime = schedule_start_datetime.astimezone(company_timezone)
            schedule_end_datetime =  schedule_end_datetime.astimezone(company_timezone)
            schedule_object = {
                'first_name': schedule.caregiver.first_name,
                'last_name': schedule.caregiver.last_name,
                'date': '{0}-{1}-{2}'.format(schedule_start_datetime.date().year,
                    schedule_start_datetime.date().month,
                    schedule_start_datetime.date().day),
                'start_time': schedule_start_datetime.time().strftime("%I:%M %p"),
                'end_time': schedule_end_datetime.time().strftime("%I:%M %p"),
                'id': schedule.id,
                'uid': str(schedule.uid)
            }
            if schedule.date == current_date:
                if schedule.caregiver in active_caregivers:
                    schedule_object['status'] = 'active'
                elif schedule.caregiver in late_caregivers:
                    schedule_object['status'] = 'late'
                elif schedule.caregiver in not_clocked_out_caregivers:
                    schedule_object['status'] = 'not_clocked_out'
                else:
                    schedule_object['status'] = 'normal'
            else:
                schedule_object['status'] = 'normal'
            schedule_objects.append(schedule_object)
        return HttpResponse(json.dumps(schedule_objects),content_type="application/json")

@login_required
def get_client_tasks_with_uids(request):
    if request.method == 'GET':
        context = {}
        company = request.user.company
        client_uids = request.GET.getlist('client_uids[]')
        current_company = request.user.company
        clients = Client.objects.filter(company=company, uid__in=client_uids)
        client_tasks = list(TaskSchedule.objects.filter(company=company,
                                client__in=clients))
        schedule_objects = []
        for schedule in client_tasks:
            schedule_object = {
                'first_name': schedule.client.first_name,
                'last_name': schedule.client.last_name,
                'activity_task': schedule.activity_task,
                'date': '{0}-{1}-{2}'.format(schedule.date.year, schedule.date.month, schedule.date.day),
                'id': schedule.id,
                'uid': str(schedule.uid),
                'pending': schedule.pending,
                'complete': schedule.complete,
                'in_progress': schedule.in_progress,
                'cancelled': schedule.cancelled
            }
            if schedule.start_time != "":
                schedule_object['start_time'] = schedule.start_time
                schedule_object['start_stamp'] = "{0}T{1}:00Z".format(schedule_object['date'],schedule.start_time)
                #datetime.datetime.strptime(schedule.start_time,'%H:%M').strftime('%I:%M %p')
            else:
                schedule_object['start_time'] = ""
                schedule_object['start_stamp'] = schedule_object['date']
            if schedule.end_time != "":
                schedule_object['end_time'] = schedule.end_time
                schedule_object['end_stamp'] = "{0}T{1}:00Z".format(schedule_object['date'],schedule.end_time)
            else:
                schedule_object['end_time'] = ""
                schedule_object['end_stamp'] = schedule_object['date']
            schedule_objects.append(schedule_object)
        return HttpResponse(json.dumps(schedule_objects),content_type="application/json")

def get_caregiver_details(request):
    company = request.user.company
    company_timezone = pytz.timezone(company.time_zone)
    current_timestamp = (timezone.now().astimezone(company_timezone))
    current_date = current_timestamp.date()
    caregivers = Caregiver.objects.filter(company=company)
    active_caregivers = list(map(lambda x: x.caregiver, CaregiverTimeSheet.objects.filter(company=company,is_active=True)))
    caregiver_schedule = CaregiverSchedule.objects.filter(company=company,date=current_date)
    (late_caregivers, not_clocked_out_caregivers) = get_late_caregivers(company, caregiver_schedule, active_caregivers, caregivers)
    #not_clocked_out_caregivers = self.get_not_clocked_out(company, caregiver_schedule, active_caregivers, caregivers)
    return (late_caregivers, not_clocked_out_caregivers, active_caregivers)

def get_late_caregivers(company, caregiver_schedule, active_caregivers, caregivers):

    late_caregivers = []
    not_clocked_out_caregivers = []

    for schedule in caregiver_schedule:
        client = schedule.client

        client_timezone = pytz.timezone(client.time_zone)
        #current_date = datetime.date.today()
        current_timestamp = (timezone.now().astimezone(client_timezone))
        current_date = current_timestamp.date()
        current_time = current_timestamp.time()

        clock_in_date = schedule.date
        clock_in_time = schedule.start_time
        clock_out_time = schedule.end_time
        if schedule.caregiver in active_caregivers:
            late_time = clock_out_time.replace(minute=clock_out_time.minute+15)
            if clock_in_date == current_date and current_time > late_time:
                not_clocked_out_caregivers.append(schedule.caregiver)
        else:
            late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
            if clock_in_date == current_date and current_time > late_time:
                late_caregivers.append(schedule.caregiver)
    return (late_caregivers, not_clocked_out_caregivers)

# This class has been written for fetching the detail locaton of the care giver
# This will be visible only to the administrator
#
class ViewCareGiverLocationLogs(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        loc_caregiver_map = []
        company = request.user.company
        locationresults = UserLocation.objects.filter(company=company)
        company_timezone = pytz.timezone(company.time_zone)
        if locationresults is not None:
            for result in locationresults:
                users = User.objects.filter(id=result.user_id)
                loc_caregiver_map.append({
                    'caregiver_name': users[0].first_name +' '+users[0].last_name,
                    'caregiver_location': 'https://www.google.com/maps/?q='+result.user_lat+','+result.user_long,
                    'date_time': result.created.astimezone(company_timezone).replace(tzinfo=None)
                })
        context['loc_caregiver_map'] = loc_caregiver_map

        return render(request, "production/caregiver_location_map.html", context)

class ServiceWorkerView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'build/js/firebase-messaging-sw.js', content_type="application/x-javascript")


#Fetch all records related to client like family, provider.

def send_call_notification(request):
    status = False
    url=""
    company = request.user.company
    if request.method == 'GET':
        user_email = request.GET.get('email')
        care_giver_user = Caregiver.objects.filter(company=company,
                                                   email_address = user_email)
        provider_user = Provider.objects.filter(company=company,
                                                email_address = user_email)
        family_user = FamilyContact.objects.filter(company=company,
                                                    email_address = user_email)

        if care_giver_user.count() > 0:
            user_token_map = UserFcmTokenMap.objects.filter(user=care_giver_user[0].user)
        elif provider_user.count() > 0:
            user_token_map = UserFcmTokenMap.objects.filter(user=provider_user[0].user)
        elif family_user.count() > 0:
            user_token_map = UserFcmTokenMap.objects.filter(user=family_user[0].user)

        if user_token_map.count() > 0:
           if user_token_map[0].fcm_token is not None:
               url = "https://appr.tc/r/"+str(randint(100000, 999999))
               data = {
                    "to": user_token_map[0].fcm_token,
                    "notification": {
                                        "body": url,
                                        "OrganizationId": "2",
                                        "priority": "high",
                                        "subtitle": "Elementary School",
                                        "Title": "hello"
                                    }
                        }
               payload= json.dumps(data)

               headers = { 'content-type': 'application/json',
                            'Authorization': 'key=AAAAUxmRa78:APA91bEvq6FZ1tJnm8FeoAxigyJ7cgoK1L4gLcAquhsZ55KQpzz1eKPx7t7bdwok4LXOtqb2OeQTWgZIpHlmbTgn7V3gs-7xwdc9Sq0828saDSJpR6k_gW1DxYMiBmbEnfoabnIfdgMc'}
               response = requests.post("https://fcm.googleapis.com/fcm/send", data=payload, headers=headers)
               if response.status_code == 200:
                    status = True
        else:
            messages.error(request, "Remote user never logged in")
    if status == True:
        return HttpResponse(url)
    elif status == False:
        return redirect('family_dashboard')


class ClientHighRisk(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        notify_client_vital_task = NotifyClientVitalTask.objects.filter(company=current_company)
        print("notify_client_vital_task",notify_client_vital_task)
        context['notify_client_vital_task'] =notify_client_vital_task


        return render(request, "production/view_client_high_risk.html", context)


def viewclienthigh( request, *args, **kwargs):
    context = {}
    id = kwargs['id']
    notify_client_vital_task = NotifyClientVitalTask.objects.get(pk= id)
    notify_client_vital_task.is_active = False
    notify_client_vital_task.save()

    return redirect("dashboard")

def admin_send_call_request_to_caregiver(request, email):
    status = False
    url=""
    caregiver_email_id = email
    company = request.user.company
    try:
        if request.method == 'GET':
            user_email = request.GET.get('email')
            care_giver_user = Caregiver.objects.get(company=company,
                                                    email_address = caregiver_email_id)


            if care_giver_user is not None:
                user_token_map = UserFcmTokenMap.objects.get(user=care_giver_user.user)




                if user_token_map is not None:

                    url = "https://appr.tc/r/"+str(randint(100000, 999999))

                    data = {
                            "to": user_token_map.fcm_token,
                            "notification": {
                                                "body": url,
                                                "OrganizationId": "2",
                                                "priority": "high",
                                                "subtitle": "Elementary School",
                                                "Title": "hello"
                                            }
                            }
                    payload= json.dumps(data)

                    headers = { 'content-type': 'application/json',
                            'Authorization': 'key=AAAAUxmRa78:APA91bEvq6FZ1tJnm8FeoAxigyJ7cgoK1L4gLcAquhsZ55KQpzz1eKPx7t7bdwok4LXOtqb2OeQTWgZIpHlmbTgn7V3gs-7xwdc9Sq0828saDSJpR6k_gW1DxYMiBmbEnfoabnIfdgMc'}
                    response = requests.post("https://fcm.googleapis.com/fcm/send", data=payload, headers=headers)
                    print("USer Map :",user_token_map.fcm_token)
                    if response.status_code == 200:
                            status = True
                else:
                    messages.error(request, "Remote user never logged in")
    except Exception as ex:
        print("Exception :", ex)

    if status == True:
        return redirect(url)
    elif status == False:
        return redirect('view_client_high_risk')


def get_clients_details(request):
    if request.method == "GET":
        user_email = request.GET.get('client_email_address')
        clients = Client.objects.filter(company=request.user.company, email_address = user_email)
        family_member =clients[0].family_contacts.all().exclude(user= request.user)
        provider = clients[0].provider.all().exclude(user= request.user)
        caregiver = clients[0].caregiver.all().exclude(user= request.user)
        context = {
              'provider' :   provider,
              'caregiver':   caregiver,
              'family_member' : family_member
       }

    return render(request, 'production/available_users_modal.html', context)


@login_required
def management_dashboard(request):
    if request.method == "GET":
        context = {}
        y_count_series = []
        x_company_name_series = []
        pie_chart=[]
        total_pending_tasks = 0
        total_completed_tasks = 0
        total_scheduled_tasks = 0
        total_client = 0
        total_high_risk_client = 0
        company_wise_pie = []
        company_wise_risk_client = []

        company_list = request.user.company.get_child_companies()
        print("Date :",datetime.date.today())
        for comp in company_list:
            high_client = NotifyClientVitalTask.objects.filter(company=comp, created__range=[datetime.date.today(),datetime.date.today()])
            x_company_name_series.append(comp.company_name)
            y_count_series.append(high_client.count())

            company_wise_pie.append({
                'company_id': "chart_"+str(comp.pk),
                'company_name': comp.company_name,
                'data_set': [TaskSchedule.objects.filter(company=comp,date__range=[datetime.date.today(),datetime.date.today()]).count(),
                            TaskSchedule.objects.filter(company=comp,pending=True,date__range=[datetime.date.today(),datetime.date.today()]).count(),
                            TaskSchedule.objects.filter(company=comp,complete=True,date__range=[datetime.date.today(),datetime.date.today()]).count()]
            })

            high_risk_client = NotifyClientVitalTask.objects.filter(company = comp)
            for risk in high_risk_client:
                company_wise_risk_client.append(risk)

            total_scheduled_tasks = total_scheduled_tasks + TaskSchedule.objects.filter(company=comp,date__range=[datetime.date.today(),datetime.date.today()]).count()
            total_pending_tasks = total_pending_tasks + TaskSchedule.objects.filter(company=comp,pending=True,date__range=[datetime.date.today(),datetime.date.today()]).count()
            total_completed_tasks = total_completed_tasks + TaskSchedule.objects.filter(company=comp,complete=True,date__range=[datetime.date.today(),datetime.date.today()]).count()

            total_client = total_client + Client.objects.filter(company = comp).count()


        total_healthy_client = total_client - len(company_wise_risk_client)
        pie_chart = [total_scheduled_tasks, total_pending_tasks, total_completed_tasks]
        context['company_details'] = request.user.company
        context['pie_chart'] = pie_chart
        context['y_count_series'] = y_count_series
        context['x_company_name_series'] = x_company_name_series
        context['company_wise_pie'] = company_wise_pie
        context['company_wise_risk_client'] = company_wise_risk_client
        context['total_healthy_client'] = total_healthy_client
        context['total_client'] = total_client
        context['total_high_risk_client'] = len(company_wise_risk_client)



    return render(request, 'production/management_dashboard.html', context)

def date_filter_management_dashboard(request):
    dashboard_data = {}
    current_company = request.user.company
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    y_count_series = []
    x_company_name_series = []
    pie_chart=[]
    total_pending_tasks = 0
    total_completed_tasks = 0
    total_scheduled_tasks = 0
    company_wise_pie = []
    company_list = Company.objects.filter(account_number__startswith=request.user.company.account_number).exclude(account_number=request.user.company.account_number)

    for comp in company_list:
        high_client = NotifyClientVitalTask.objects.filter(company=comp, created__range=[start_date,end_date])
        x_company_name_series.append(comp.company_name)
        y_count_series.append(high_client.count())
        total_scheduled_tasks = total_scheduled_tasks + TaskSchedule.objects.filter(company=comp,date__range=[start_date,end_date]).count()
        total_pending_tasks = total_pending_tasks + TaskSchedule.objects.filter(company=comp,pending=True,date__range=[start_date,end_date]).count()
        total_completed_tasks = total_completed_tasks + TaskSchedule.objects.filter(company=comp,complete=True,date__range=[start_date,end_date]).count()


        company_wise_pie.append({
                'company_id': "chart_"+str(comp.pk),
                'company_name': comp.company_name,
                'data_set': [TaskSchedule.objects.filter(company=comp,date__range=[start_date,end_date]).count(),
                            TaskSchedule.objects.filter(company=comp,pending=True,date__range=[start_date,end_date]).count(),
                            TaskSchedule.objects.filter(company=comp,complete=True,date__range=[start_date,end_date]).count()]
        })





    pie_chart = [total_scheduled_tasks, total_pending_tasks, total_completed_tasks]
    dashboard_data['company_wise_pie'] = company_wise_pie
    dashboard_data['pie_chart'] = pie_chart
    dashboard_data['total_pending_tasks'] = total_pending_tasks
    dashboard_data['total_pending_tasks'] = total_pending_tasks
    dashboard_data['total_scheduled_tasks'] = total_scheduled_tasks
    dashboard_data['y_count_series'] = y_count_series
    dashboard_data['x_company_name_series'] = x_company_name_series


    return HttpResponse(json.dumps(dashboard_data),content_type="application/json")



class CompanyHoliday(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        context['company_holiday_form'] = CompanyHolidayForm()
        company_holidays =  CompanyHolidays.objects.filter(company=current_company)
        context['company_holidays'] = company_holidays
        context["delete_holiday_form"] = DeleteHolidayForm()
        return render(request, 'production/company_holiday.html', context)



    def post(self, request):
        context = {}
        current_company = request.user.company
        company_holiday_form = CompanyHolidayForm(request.POST)

        if company_holiday_form.is_valid():
            holiday_name = company_holiday_form.cleaned_data['holiday_name']
            description = company_holiday_form.cleaned_data['description']
            date = company_holiday_form.cleaned_data['eventDate']
            company_holiday = CompanyHolidays(company = current_company,
                                              holiday_name = holiday_name,description=description,
                                              date = date)
            company_holiday.save()
            messages.success(request, "Holiday successfully added")
        return HttpResponseRedirect(reverse('company_holiday'))



@login_required
def view_company_holiday_id(request):

    if request.method == 'GET':
        context = {}
        current_company = request.user.company
        holiday_id = request.GET.get('holiday_id')
        current_holiday = CompanyHolidays.objects.get(company =current_company,id =holiday_id)
        holiday_id = current_holiday.id
        holiday_name = current_holiday.holiday_name
        description  = current_holiday.description
        holiday_date = current_holiday.date


        holiday_data = {
            'holiday_id':holiday_id,
            'holiday_name' : holiday_name,
            'description' : description,
            'date' : "{0}/{1}/{2}".format(holiday_date.month,holiday_date.day,holiday_date.year)
        }
        return HttpResponse(json.dumps(holiday_data), content_type="application/json")


@login_required
def delete_holiday_with_id(request):

    if request.method == 'POST':
        context = {}
        company = request.user.company
        holiday_id = request.POST.get('holiday_id')
        current_holiday = CompanyHolidays.objects.get(company=company, id = holiday_id)
        current_holiday.delete()
        return HttpResponse("Delete Successful")


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
        
    return None

@login_required
def generate_pdf(request):
    data ={}
    context = request.GET.copy()

    current_company = request.user.company
    request.session['context'] = context
    company_name  = request.GET.get('company_name')
    company_address  = request.GET.get('company_address')
    company_city  = request.GET.get('company_city')
    company_state  = request.GET.get('company_state')
    company_zipcode  = request.GET.get('company_zipcode')
    company_contactnumber  = request.GET.get('company_contactnumber')
    start_date  = request.GET.get('start_date')
    end_date  = request.GET.get('end_date')
    client_firstname  = request.GET.get('client_firstname')
    client_lastname  = request.GET.get('client_lastname')
    client_address  = request.GET.get('client_address')
    client_city  = request.GET.get('client_city')
    client_zipcode  = request.GET.get('client_zipcode')
    client_state  = request.GET.get('client_state')
    client_contact_number  = request.GET.get('client_contact_number')
    total  = request.GET.get('total')
    total_cost  = request.GET.get('total_cost')
    company_logo  = request.GET.get('company_logo')
    invoice_notes  = request.GET.get('invoice_notes')
    invoice_number_string  = request.GET.get('invoice_number_string')
    company_address = request.GET.get('company_address')
    invoice_header_id = request.GET.get('invoice_header_id')
    return redirect('get_pdf')


def get_pdf(request):
    current_company = request.user.company
    invoice_headerid = request.session.get('context').get('invoice_header_id')
    start_date = request.session.get('context').get('start_date')
    end_date = request.session.get('context').get('end_date')
    current_date = datetime.date.today()    
    invoice_header = InvoiceHeader.objects.get(id = invoice_headerid )
    caregiver_schedule_notes = CaregiverSchedule.objects.filter(company = current_company, client = invoice_header.client, date__range = (invoice_header.start_date, invoice_header.end_date))
    invoice_line_items =list(InvoiceLineItem.objects.filter(invoice_header = invoice_header,company =current_company))
    data = {
        
        "invoice_header" : invoice_header,
        "invoice_line_items" : invoice_line_items,
        "start_date": start_date,
        "end_date": end_date,
        "current_date": current_date,
        "current_company": current_company,
        "caregiver_schedule_notes":caregiver_schedule_notes
    }
    
    pdf = render_to_pdf('production/invoice_generator.html',data)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')        
        filename = "Invoice_{}.pdf".format(request.session.get('context').get('company_name'))
        content = "inline; filename={}".format(filename)
        content = "attachment; filename={}".format(filename)
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")

@login_required
def submit_invoice(request):
    if request.method == "GET":
        current_company = request.user.company
        context = request.GET.copy()
        invoice_notes  = request.GET.get('invoice_notes')
        invoice_header_id  = request.GET.get('invoice_header_id')
        invoice_headerlist  =  json.loads(request.GET.get('invoice_field_array'))
        client_email  = request.GET.get('email')
        invoice_header = InvoiceHeader.objects.get(id =invoice_header_id)
        invoice_header.invoice_notes = invoice_notes
        invoice_header.save()
        start_date = invoice_header.start_date
        end_date = invoice_header.end_date
        invoiceadd = {
            "client_email" :client_email
        }
        for k in invoice_headerlist:
            caregiverid = k['caregiverid']
            invoice_fieldrate_type = k['invoice_fieldrate_typeid']
            caregiver = Caregiver.objects.get(id= caregiverid, company = current_company)
            invoice_fieldrate = float(k['invoice_fieldrate'])
            invoice_header = InvoiceHeader.objects.get(id =invoice_header_id)
            ratetypes = InvoiceRateType.objects.get(id = invoice_fieldrate_type)
            if current_company.mileage_rate and ratetypes.rate_types == "Mileage":

                inline_total = (float(invoice_fieldrate) * float(current_company.mileage_rate))/100
                
                if inline_total > 0:
                    new_invoice_line = InvoiceLineItem(invoice_header = invoice_header,  company = current_company,
                                                       rate_type = ratetypes.rate_types,
                                                       hours = 0,
                                                       caregiver = caregiver,
                                                       rate =invoice_fieldrate,
                                                       total =  inline_total)
                    new_invoice_line.save()                                                                       
                    
                    invoice_header.total_cost = invoice_header.total_cost + Decimal.from_float(inline_total)
                    invoice_header.save()
            else:
                invoice_line = InvoiceLineItem(invoice_header = invoice_header,  company = current_company,
                                                       rate_type = ratetypes.rate_types,
                                                       hours = 0,
                                                       caregiver = caregiver,
                                                       rate =invoice_fieldrate,
                                                       total =  invoice_fieldrate)
                invoice_line.save()
                invoice_header.total_cost = invoice_header.total_cost + Decimal.from_float(invoice_fieldrate)
                invoice_header.save()
   
    return HttpResponse(json.dumps(invoiceadd), content_type="application/json")

@login_required
def cancel_invoice(request):
    if request.method == "GET":
        current_company = request.user.company
        
        context = request.GET.copy()
        invoice_id = request.GET.get('invoice_id')
        invoice_header = InvoiceHeader.objects.get(id = invoice_id )
        invoice_header.cancelled = True
        invoice_header.save()

    return HttpResponseRedirect(reverse('choose_client_for_invoice'))

@login_required
def update_invoice_detail(request):
    if request.method == "GET":
        
        current_company = request.user.company
        
        context = request.GET.copy()
        invoice_linelist  =  json.loads(request.GET.get('invoice_line_array'))
        
        ratetype = request.GET.get('ratetype')        
        data = {
            "ratetype" : "sucess"
        }

        for i in invoice_linelist:
            invoice_line_id = int(i['invoic_line_id'])
            change_hours = float(i['change_hours'])
            change_ratetype = i['change_ratetype']
            change_rate = float(i['change_rate'])
            invoice_line_item = InvoiceLineItem.objects.get(id = invoice_line_id)
            invoice_line_hours =  invoice_line_item.hours
            invoice_line_total = invoice_line_item.total
            invoice_line_rate = invoice_line_item.rate
            
            invoice_header = InvoiceHeader.objects.get(id = invoice_line_item.invoice_header.id)
            invoice_header_total = float(invoice_header.total_cost) - float(invoice_line_total)
            invoice_header.total_cost = float(invoice_header_total)
            invoice_header_total_hours =  float(invoice_header.total_hours) - float(invoice_line_hours)
            invoice_header.total_hours = invoice_header_total_hours
            invoice_header.save()
            invoice_line_item.hours = change_hours
            invoice_line_item.rate = change_rate
            invoice_line_item.rate_type = change_ratetype
            invoice_line_item.total = float(change_hours) * float(change_rate)
            invoice_header.total_cost =  float(invoice_header.total_cost) + float(invoice_line_item.total)
            invoice_header.total_hours =  float(invoice_header.total_hours) + float(invoice_line_item.hours)
            if invoice_header.taxes:
                invoice_header.total_cost = invoice_header.total_cost - float(invoice_header.taxes)
                tax_amt= round((invoice_header.total_cost * float(current_company.tax_rate / 100)),2)
                invoice_header.taxes = tax_amt
                invoice_header.total_cost =  (invoice_header.total_cost * 1) +  float(tax_amt)
            invoice_header.save()
            invoice_line_item.save()
          

        return HttpResponse(json.dumps(data), content_type="application/json")



class CompanyCrm(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        lead_detail = CrmClientLead.objects.filter(company = current_company)
        context['lead_detail'] = lead_detail
        
        return render(request, 'production/company_crm_home.html', context)



class AddCrmLead(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        current_company = Company.objects.get(company_id = current_company.company_id)
        context['current_company'] = current_company    
        context['crm_lead_form'] = CrmLeadForm()
        return render(request, 'production/add_crm_client_lead.html', context)
    
    def post(self,request):
        
        context = {}
        current_company = request.user.company
        crm_lead_form = CrmLeadForm(request.POST)
        context['crm_lead_form'] = crm_lead_form
        if crm_lead_form.is_valid():
            lead_owner = crm_lead_form.cleaned_data['lead_owner']
            lead_first_name = crm_lead_form.cleaned_data['lead_first_name']
            lead_last_name = crm_lead_form.cleaned_data['lead_last_name']
            lead_gender = crm_lead_form.cleaned_data['lead_gender']
            phone_number = crm_lead_form.cleaned_data['phone_number']
            lead_date_of_birth = crm_lead_form.cleaned_data['date_of_birth']
            secondary_phone_number = crm_lead_form.cleaned_data['secondary_phone_number']
            lead_email = crm_lead_form.cleaned_data['lead_email']
            city = crm_lead_form.cleaned_data['city']
            state = crm_lead_form.cleaned_data['state']
            zip_code = crm_lead_form.cleaned_data['zip_code']
            lead_status = crm_lead_form.cleaned_data['lead_status']
            lead_source = crm_lead_form.cleaned_data['lead_source']
            lead_address = crm_lead_form.cleaned_data['lead_address']
            lead_discription = crm_lead_form.cleaned_data['lead_discription']
            try:
                lead_crm = CrmClientLead(company = current_company,
                                         lead_owner = lead_owner,
                                         lead_last_name = lead_last_name,
                                         lead_first_name = lead_first_name,
                                         gender = lead_gender,
                                         lead_contact_number = phone_number,
                                         lead_date_of_birth = lead_date_of_birth,
                                         lead_secondary_phone_number =secondary_phone_number,
                                         lead_email_address = lead_email,
                                         lead_source =lead_source,
                                         lead_status= lead_status,
                                         lead_state= state,
                                         lead_city = city,
                                         lead_zip_code = zip_code,
                                         lead_address =lead_address,
                                         description = lead_discription)
                                        
                lead_crm.save()
                messages.success(request, "Lead successfully added. Add additional Details Below.")
            except IntegrityError as e:
                messages.error(request, "Lead already exists. Please enter a new Client.")
        return HttpResponseRedirect(reverse('company_crm'))

    def parse_date(self,client_birthday):
        output_month = client_birthday.month
        output_day = client_birthday.day
        output_year = client_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string
            



class CrmNotesFollowUP(LoginRequiredMixin, View):

    def get(self, request,*args, **kwargs):
        context = {}
        id = kwargs['id']
        lead_details = CrmClientLead.objects.get(pk = id)
        context['lead_details'] = lead_details
        current_company = Company.objects.get(pk = lead_details.company_id)
        context['current_company'] = current_company
        crm_lead_notes = CrmNotes.objects.filter(crm_client =lead_details)
        context['crm_lead_notes'] = crm_lead_notes     
        return render(request, 'production/crm_notes_follow_up.html', context)

@login_required
def savecrm_notes(request):
    if request.method == "GET":
        context = {}
        current_company = request.user.company
        lead_details_id  =  json.loads(request.GET.get('lead_details_id'))
        lead_details_notes = json.dumps(request.GET.get('lead_details_notes'))
        lead_details = CrmClientLead.objects.get(id =  lead_details_id)
        lead_details_notes = json.loads(lead_details_notes)

        crm_notes = CrmNotes(company = current_company,crm_client = lead_details, notes = lead_details_notes)

        crm_notes.save()
        
        crm_lead_notes = CrmNotes.objects.filter(crm_client =lead_details )
        context['crm_lead_notes'] = crm_lead_notes
        data = {
            "data" : "sucess"
        }
        return HttpResponse(json.dumps(data), content_type="application/json")



@login_required
def update_lead_status(request):
    if request.method == "GET":
        context = {}
        current_company = request.user.company
        lead_details_id  =  json.loads(request.GET.get('lead_details_id'))
        lead_status = json.dumps(request.GET.get('lead_status'))
        lead_details = CrmClientLead.objects.get(id =  lead_details_id)
        lead_status = json.loads(lead_status)
        crm_lead_detail = CrmClientLead.objects.get(id = lead_details_id)
        crm_lead_detail.lead_status = lead_status
        crm_lead_detail.save()
        data = {
            "data" : "sucess"
        }
        return HttpResponse(json.dumps(data), content_type="application/json")



class LeadDelete(LoginRequiredMixin, View):
    
    def get(self, request,*args, **kwargs):
        context = {}
        id = kwargs['id']
        lead_details = CrmClientLead.objects.get(id = id).delete()
        return HttpResponseRedirect(reverse('company_crm'))



@login_required
def convert_lead(request):
    if request.method == "GET":
        current_company = request.user.company
        
        context = request.GET.copy()
        lead_id = request.GET.get('lead_id')
        lead_crm = CrmClientLead.objects.get(id = lead_id )
        try:
            lead_email = lead_crm.lead_email_address
            new_client = Client(company = current_company,
                                email_address = lead_crm.lead_email_address,
                                first_name = lead_crm.lead_first_name,
                                last_name = lead_crm.lead_last_name,
                                gender = lead_crm.gender,
                                date_of_birth = lead_crm.lead_date_of_birth,
                                phone_number = lead_crm.lead_contact_number,
                                secondary_phone_number = lead_crm.lead_secondary_phone_number,
                                address = lead_crm.lead_address,
                                city = lead_crm.lead_city,
                                state = lead_crm.lead_state,
                                zip_code = lead_crm.lead_zip_code
                                )
            
            new_client.save()
            
            
            
            messages.success(request, "Lead {0} {1} successfully Converted To Client!".format( lead_crm.lead_first_name, lead_crm.lead_last_name))
            lead_crm = CrmClientLead.objects.get(id = lead_id ).delete()
            return HttpResponseRedirect(reverse('edit_client') + "?client_email=" +  lead_email)
            
        except IntegrityError as e:
            messages.error(request, "Client already exists. Please enter a new client.")
    return HttpResponseRedirect(reverse('company_crm'))



class EditCrmLead(LoginRequiredMixin, View):
    
    def get(self, request,*args, **kwargs):
        context = {}
        current_company = request.user.company
        lead_email = request.GET.get('lead_email')
        lead_details = CrmClientLead.objects.get(company = current_company,lead_email_address = lead_email)
        # lead_id = request.GET.get('lead_id')
       
        current_company = Company.objects.get(company_id = current_company.company_id)
        context['current_company'] = current_company    
        
        

        if lead_details:
            lead_details = CrmClientLead.objects.get(id = lead_details.id)
            current_company = request.user.company
            current_company = Company.objects.get(company_id = current_company.company_id)
            
            crm_lead_form = CrmLeadForm(initial=
            {
             "lead_first_name" : lead_details.lead_first_name,
             "lead_last_name"  :lead_details.lead_last_name,
             "lead_email" : lead_details.lead_email_address,
             "lead_gender" : lead_details.gender,
             "lead_address" : lead_details.lead_address,
             "city": lead_details.lead_city,
             "state": lead_details.lead_state,
             "zip_code":lead_details.lead_zip_code,
             "phone_number":lead_details.lead_contact_number,
             "date_of_birth" : self.parse_date(lead_details.lead_date_of_birth),
             "secondary_phone_number":lead_details.lead_secondary_phone_number,
             "lead_status":lead_details.lead_status,
             "lead_source":lead_details.lead_source,
             "lead_discription":lead_details.description
            })
            context['crm_lead_form'] = crm_lead_form
            # context['lead_value'] = lead_id
            context['lead_email'] = lead_details.lead_email_address
        return render(request, 'production/edit_crm_lead.html', context)

    def post(self,request):
        context = {}
        current_company = request.user.company
        crm_lead_form = CrmLeadForm(request.POST)
        context['crm_lead_form'] = crm_lead_form        
        email =  crm_lead_form.data['lead_email']
        if crm_lead_form.is_valid():
            lead_client = CrmClientLead.objects.get(lead_email_address = email)
            lead_client.lead_first_name = crm_lead_form.cleaned_data['lead_first_name']
            lead_client.lead_last_name = crm_lead_form.cleaned_data['lead_last_name']
            lead_client.lead_date_of_birth = crm_lead_form.cleaned_data['date_of_birth']
            lead_client.gender = crm_lead_form.cleaned_data['lead_gender']
            lead_client.lead_source =  crm_lead_form.cleaned_data['lead_source']
            lead_client.lead_contact_number =  crm_lead_form.cleaned_data['phone_number']
            lead_client.lead_secondary_phone_number =crm_lead_form.cleaned_data['secondary_phone_number']
            lead_client.lead_status = crm_lead_form.cleaned_data['lead_status']
            lead_client.lead_address = crm_lead_form.cleaned_data['lead_address']
            lead_client.lead_city = crm_lead_form.cleaned_data['city']
            lead_client.lead_state = crm_lead_form.cleaned_data['state']
            lead_client.lead_zip_code = crm_lead_form.cleaned_data['zip_code']
            lead_client.description = crm_lead_form.cleaned_data['lead_discription']
            lead_client.save()
            messages.success(request, "Lead {0} {1} successfully edited!".format(lead_client.lead_first_name,lead_client.lead_last_name))

        return HttpResponseRedirect(reverse('edit_crm_lead') + "?lead_email=" + lead_client.lead_email_address)
        
    def parse_date(self,client_birthday):
        if client_birthday:
            output_month = client_birthday.month
            output_day = client_birthday.day
            output_year = client_birthday.year
            output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
            return output_string


def render_to_pdfs(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    output_filename = "mycareportal_app/download_invoice_pdf/Invoice.pdf"
    result_file = open(output_filename, "w+b")
    file = open('mycareportal_app/download_invoice_pdf/Invoice.pdf', "w+b")
    pdf = pisa.pisaDocument(html.encode('utf-8'), dest=file,encoding='utf-8')
    file.seek(0)
    pdf = file.read()               
    file.close()
    
    return None

@login_required
def send_email_invoice(request):

    if request.method == "GET":
        data ={}
        context = request.GET.copy()
        user = request.user
        current_company = request.user.company
        request.session['context'] = context
        invoice_header_id = request.GET.get('invoice_header_id')
        start_date  = request.GET.get('start_date')
        end_date  = request.GET.get('end_date')
        current_date = datetime.date.today()
        invoice_header = InvoiceHeader.objects.get(id = invoice_header_id )
        caregiver_schedule_notes = CaregiverSchedule.objects.filter(company = current_company, client = invoice_header.client, date__range = (invoice_header.start_date, invoice_header.end_date))
        invoice_line_items =list(InvoiceLineItem.objects.filter(invoice_header = invoice_header,company =current_company))
        data = {
            "invoice_header" : invoice_header,
            "invoice_line_items" : invoice_line_items,
            "start_date": start_date,
            "end_date": end_date,
            "current_date": current_date,
            "current_company": current_company,
            "caregiver_schedule_notes":caregiver_schedule_notes
        }

        post_pdf = render_to_pdfs('production/invoice_generator.html',data)
        toemail = invoice_header.client.email_address
        client = Client.objects.get(email_address = toemail)
        
        email_manager = CareManagerEmailProcessor()
        email_manager.send_invoice_mail_by_caremanager(user,current_company,client)
        invoiceadd = {
            "client_email" :invoice_header.client.email_address
        }
        
        
    return HttpResponse(json.dumps(invoiceadd), content_type="application/json")
            
     

class ChooseCaregiverPayroll(LoginRequiredMixin, View):
    
    def get(self, request,*args, **kwargs):
        context = {}
        current_company = request.user.company
        context['current_company'] = current_company
        context['choose_caregiver_payroll_form'] = ChooseCaregiverPayrollForm()
        all_caregivers = Caregiver.objects.all()
        payroll_header = PayrollHeader.objects.filter(company=current_company,submitted = True,cancelled =False)
        context['payroll_header'] = payroll_header

        context['all_caregivers'] = all_caregivers
        return render(request, 'production/choose_caregiverpayroll.html', context)
    
  


class Payroll(LoginRequiredMixin, View):
    
    
    def get(self, request,*args, **kwargs):
        context = {}
        payroll_id = request.GET.get('payroll_id')
        current_company = request.user.company
        context['current_company'] = current_company
        current_date = datetime.date.today()
        context['current_date'] =current_date
        if payroll_id:
            submit = True
            context['submit'] = submit
            exits_invoice_header = PayrollHeader.objects.filter(company = current_company, id = payroll_id,  submitted = True,cancelled =False)
            context['payroll_header'] = exits_invoice_header
            payroll_header = PayrollHeader.objects.filter(id = exits_invoice_header)
            context['payroll_header'] = payroll_header
            payroll_line_item = []
            for i in payroll_header:
                payroll_item = PayrollLineItem.objects.filter(payroll_header = i.id)
                payroll_line_item.append(payroll_item)
                payroll_header = PayrollHeader.objects.get(id = i.id)
                context['payroll_header'] = payroll_header
                context['payroll_line_item'] = payroll_line_item
            # payroll_line_item = PayrollLineItem.objects.filter(payroll_header = payroll_header,company = current_company).order_by("id")
            # context['payroll_line_item'] = payroll_line_item
            # caregiver_schedule_notes = CaregiverSchedule.objects.filter(company = current_company, client= invoice_header_data.client, date__range = (invoice_header_data.start_date, invoice_header_data.end_date))
            # context['caregiv  er_schedule_notes'] = caregiver_schedule_notes
        else:
            submit = False
            context['submit'] = submit
            caregiver = Caregiver.objects.filter(company = current_company )
            context['caregiver'] = caregiver
            invoice_rate_types = InvoiceRateType.objects.all()
            context['invoice_rate_types'] = invoice_rate_types
            choose_caregiver_payroll_form = ChooseCaregiverPayrollForm(request.GET)
            if choose_caregiver_payroll_form.is_valid():
                # caregiver_email = choose_caregiver_payroll_form.cleaned_data['caregiver_email']
                # caregiver = Caregiver.objects.get(company=current_company, email_address=caregiver_email)
                start_date = choose_caregiver_payroll_form.cleaned_data['start_date']
                end_date = choose_caregiver_payroll_form.cleaned_data['end_date']
                # context['caregiver'] = caregiver
                context['start_date'] = start_date
                context['end_date'] = end_date
                caregivers = Caregiver.objects.filter(company= current_company)
                exits_payroll_header = PayrollHeader.objects.filter(company = current_company, start_date = start_date,end_date = end_date ,  submitted = True, cancelled = False)
                if exits_payroll_header:
                    
                    payroll_headers = list(PayrollHeader.objects.filter(start_date = start_date,end_date = end_date ,  submitted = True, cancelled = False))
                    # context['payroll_header'] = payroll_headers
                    payroll_line_item = []
                    for i in payroll_headers: 
                        payroll_item = PayrollLineItem.objects.filter(payroll_header = i.id)
                        payroll_line_item.append(payroll_item)
                        payroll_header = PayrollHeader.objects.get(id = i.id)
                        context['payroll_header'] = payroll_header
                        context['payroll_line_item'] = payroll_line_item
                else:
                    
                    for caregiver in caregivers:
                        payroll_header = PayrollHeader.create_payroll(current_company,caregiver,start_date,end_date)
                        payroll_header = list(PayrollHeader.objects.filter(start_date = start_date,end_date = end_date ,  submitted = True,cancelled= False))
                        context['payroll_header'] = payroll_header
                        payroll_line_item = []
                        for i in payroll_header: 
                            payroll_item = PayrollLineItem.objects.filter(payroll_header = i.id)
                            payroll_line_item.append(payroll_item)
                            payroll_header = PayrollHeader.objects.get(id = i.id)
                            context['payroll_header'] = payroll_header
                            context['payroll_line_item'] = payroll_line_item

        return render(request, 'production/payroll.html', context)



@login_required
def update_payroll_detail(request):
    if request.method == "GET":
        
        current_company = request.user.company
        
        context = request.GET.copy()
        payroll_linelist  =  json.loads(request.GET.get('payroll_line_array'))
        ratetype = request.GET.get('ratetype')           
        data = {
            "ratetype" : "sucess"
        }
        for i in payroll_linelist:
            invoice_line_id = int(i['payroll_line_id'])
            change_hours = float(i['change_hours'])
            change_ratetype = i['change_ratetype']
            change_rate = float(i['change_rate'])
            payroll_line_item = PayrollLineItem.objects.get(id = invoice_line_id)
            payroll_line_hours =  payroll_line_item.hours
            payroll_line_total = payroll_line_item.total
            payroll_line_rate = payroll_line_item.rate
            payroll_header = PayrollHeader.objects.get(id = payroll_line_item.payroll_header.id)
            payroll_header_total = float(payroll_header.total_cost) - float(payroll_line_total)
            payroll_header_total_hours =  float(payroll_header.total_hours) - float(payroll_line_hours)
            payroll_header.total_cost = float(payroll_header_total)
            payroll_header.total_hours =  float(payroll_header_total_hours)
            payroll_header.save()
            payroll_line_item.hours = change_hours
            payroll_line_item.rate = change_rate
            payroll_line_item.rate_type = change_ratetype
            payroll_line_item.total = float(change_hours) * float(change_rate)
            payroll_header.total_cost =  float(payroll_header.total_cost) + float(payroll_line_item.total)
            payroll_header.total_hours = float(payroll_header.total_hours) +  float(payroll_line_item.hours)
            # if invoice_header.taxes:
            #     invoice_header.total_cost = invoice_header.total_cost - float(invoice_header.taxes)
            #     tax_amt= round((invoice_header.total_cost * float(current_company.tax_rate / 100)),2)
            #     invoice_header.taxes = tax_amt
            #     invoice_header.total_cost =  (invoice_header.total_cost * 1) +  float(tax_amt)
            payroll_header.save()
            payroll_line_item.save()
          

        return HttpResponse(json.dumps(data), content_type="application/json")









@login_required
def submit_payroll(request):
    if request.method == "GET":
        current_company = request.user.company
        context = request.GET.copy()
        payroll_notes  = request.GET.get('payroll_notes')
        payroll_header_id  = request.GET.get('payroll_header_id')
        payroll_headerlist  =  json.loads(request.GET.get('invoice_field_array'))
        client_email  = request.GET.get('email')
        payroll_header = PayrollHeader.objects.get(id =payroll_header_id)
        
        payroll_header.save()

        start_date = payroll_header.start_date
        end_date = payroll_header.end_date
        
        invoiceadd = {
            "client_email" :client_email
        }
        for k in payroll_headerlist:
            
            caregiverid = k['caregiverid']
            invoice_fieldrate_type = k['invoice_fieldrate_typeid']
            caregiver = Caregiver.objects.get(id = caregiverid, company = current_company)
            invoice_fieldrate = float(k['invoice_fieldrate'])
            payroll_header = PayrollHeader.objects.get(id =payroll_header_id)
            payroll_header =PayrollHeader.objects.filter(start_date = payroll_header.start_date , end_date = payroll_header.end_date )
            for i in payroll_header:
                if caregiver.id == i.caregiver.id:
                    caregiver = Caregiver.objects.get(id = i.caregiver.id, company = current_company)
                    ratetypes = InvoiceRateType.objects.get(id = invoice_fieldrate_type)
                    payroll_header = PayrollHeader.objects.get(company = current_company,id = i.id)
                    if current_company.mileage_rate and ratetypes.rate_types == "Mileage":
                        inline_total = (float(invoice_fieldrate) * float(current_company.mileage_rate))/100
                        if inline_total > 0:
                            new_payroll_line = PayrollLineItem(payroll_header = payroll_header,  company = current_company,
                                                           rate_type = ratetypes.rate_types,
                                                           hours = 0,
                                                           caregiver = caregiver,
                                                           rate = invoice_fieldrate,
                                                           total =  inline_total)
                            new_payroll_line.save()                                                                       
                            i.total_cost = i.total_cost + Decimal.from_float(inline_total)
                            i.save()
                    else:
                        payroll_line = PayrollLineItem(payroll_header = payroll_header,  company = current_company,
                                                       rate_type = ratetypes.rate_types,
                                                       hours = 0,
                                                       caregiver = caregiver,
                                                       rate =invoice_fieldrate,
                                                       total =  invoice_fieldrate)
                        payroll_line.save()
                        i.total_cost = i.total_cost + Decimal.from_float(invoice_fieldrate)
                        i.save()
   
    return HttpResponse(json.dumps(invoiceadd), content_type="application/json")


@login_required    
def generate_payroll_excel(request):

    context ={}
    context = request.GET.copy()
    current_company = request.user.company
    request.session['context'] = context  
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    payroll_header_id = request.GET.get('payroll_header_id')
    
    invoiceadd = {
            "client_email" : "vall"
    }
    if payroll_header_id:
        return redirect('getpayroll_excel')
    


def getpayroll_excel(request):
    current_company = request.user.company
    payroll_header_id = request.session.get('context').get('payroll_header_id')
    start_date = request.session.get('context').get('start_date')
    end_date = request.session.get('context').get('end_date')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="CaregiverPayroll.xls"'
        
    payroll = PayrollHeader.objects.get(id = payroll_header_id)
    payroll_header = list(PayrollHeader.objects.filter(start_date = payroll.start_date,end_date = payroll.end_date))
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Caregiver Payroll')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = [ 'Employee Name','From Period','To Period','Hours', 'Rate Type','Rate','Total' ]
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) 
    font_style = xlwt.XFStyle()
    caregivers = Caregiver.objects.filter(company= current_company)
    for caregiver in caregivers:
        payroll_header = list(PayrollHeader.objects.filter(start_date = payroll.start_date,end_date = payroll.end_date ,  submitted = True))
        payroll_line_item = []
        for i in payroll_header: 
            payroll_item = PayrollLineItem.objects.filter(payroll_header = i.id)
            payroll_line_item.append(payroll_item)
    
        
    for i in payroll_line_item:
        for row in i.values_list('caregiver','payroll_header','caregiver','hours', 'rate_type','rate','total'):
            row_num += 1
            for col_num in range(len(row)):
                if col_num == 0:
                    caregiver = Caregiver.objects.get(id = row[col_num])
                    # row[col_num] = tuple(caregiver.first_name )
                    ws.write(row_num, col_num, (caregiver.first_name," ",caregiver.last_name) )
                elif col_num == 1:

                    payroll = PayrollHeader.objects.get(id = row[col_num])
                    # date_time = datetime.datetime.strptime(cr_date, '%Y-%m-%d %H:%M:%S.%f')
                    date_time =  payroll.start_date.strftime('%Y-%m-%d')
                    end_time =  payroll.end_date.strftime('%Y-%m-%d')
                    ws.write(row_num, col_num, (date_time))
                    ws.write(row_num, 2, (end_time))
            
                elif col_num > 2:
                    ws.write(row_num, col_num, row[col_num])
    
    wb.save(response)
    
    
    return response
  

@login_required
def cancel_payroll(request):
    if request.method == "GET":
        current_company = request.user.company
        
        context = request.GET.copy()
        payroll_id = request.GET.get('payroll_id')
        payroll_header = PayrollHeader.objects.get(id = payroll_id )
        payroll_header.cancelled = True
        payroll_header.save()

    return HttpResponseRedirect(reverse('caregiverpayroll'))
