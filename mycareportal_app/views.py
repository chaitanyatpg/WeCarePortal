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
# Create your views here.

#@receiver(pre_save, sender=User)
#def user_sign_up_(sender, instance, **kwargs):
#    if instance._state.adding:
#        instance.is_active = False

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
        exception_flag = False
        #Create company object and save
        with transaction.atomic():
            try:
                new_company = Company(company_name=company_name,
                                            contact_number=contact_number,
                                            address=address,
                                            city=city,
                                            state=state,
                                            zip_code=zip_code,
                                            time_zone=time_zone)
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
    #Add company details to context
    context['company_details'] = company_details
    context['company_created_date'] = current_company.created
    days_since_company_created = (timezone.now() - current_company.created).days
    context['days_since_company_created'] = days_since_company_created
    context['current_date'] = '{0}-{1}-{2}'.format(current_date.year,current_date.strftime('%m'),current_date.strftime('%d'))
    print(context['current_date'])
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
            'time_zone': current_company.time_zone
        })
        context['company_edit_form'] = company_edit_form
        context['current_company'] = current_company
        context['all_timezones'] = pytz.all_timezones
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
                current_company.time_zone = company_edit_form.cleaned_data['time_zone']
                print(current_company.time_zone)
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
