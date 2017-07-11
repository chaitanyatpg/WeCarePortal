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

# Create your views here.

@login_required
def home(request):
    context = {}
    current_company = request.user.company
    user = request.user
    user_roles = UserRoles.objects.filter(user=user)
    user_roles = [x.role for x in user_roles]
    if "CAREMANAGER" in user_roles:
        return redirect('dashboard')
    elif "CAREGIVER" in user_roles:
        return redirect('caregiver_dashboard')
    elif "FAMILYUSER" in user_roles:
        return redirect('family_dashboard')
    else:
        return redirect('login')

def login(request):
    return render(request, 'production/wecare_login.html')

@login_required
def logout_view(request):
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
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        username = form.cleaned_data['email']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        #Create company object and save
        new_company = Company(company_name=company_name,
                                    contact_number=contact_number,
                                    address=address)
        new_company.save()
        #Create care manager user auth object and save
        new_user = User.objects.create_user(username=username,
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password,
                                            company=new_company)
        new_user.save()
        #Create care manager object and save
        new_care_manager = CareManager(user=new_user,
                                       company=new_company,
                                       email_address=email)
        new_care_manager.save()
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
        'address' : current_company.address
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
        context['add_care_manager_form'] = CareManagerRegistrationForm();
        return render(request, 'production/add_care_manager.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        add_care_manager_form = CareManagerRegistrationForm(request.POST)
        if add_care_manager_form.is_valid():
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
        context['add_care_manager_form'] = CareManagerRegistrationForm();
        return render(request, 'production/add_care_manager.html', context)

def set_tablet_id_session(request):
    if request.method == 'GET':
        tablet_id = request.GET.get('tablet_id')
        request.session["tablet_id"] = tablet_id
        return HttpResponse("Set Tablet ID")
