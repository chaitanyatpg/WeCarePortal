from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from mycareportal_app.models import *
from mycareportal_app.move_manage_forms import *
from django.views.generic import View

from django.contrib import messages

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from mycareportal_app.common import error_messaging as error_messaging
from django.contrib.sites.shortcuts import get_current_site

from mycareportal_app.email.move_manager.move_manager_email_processor import MoveManagerEmailProcessor

from django.db import transaction
from django.shortcuts import redirect
import json
from django.core.urlresolvers import reverse


def move_manager_dashboard(request):
    return render(request, 'production/move_manager_dashboard.html')

def view_move_projects(request):
    return render(request, 'production/update_move_projects.html')

def view_move_bids(request):
    return render(request, 'production/view_move_bids.html')

class AddMoveManager(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        context['move_manager_form'] = MoveManagerRegistrationForm()
        return render(request,'production/add_move_manager.html', context)

    @transaction.atomic
    def post(self, request):
        context = {}
        add_move_manager_form = MoveManagerRegistrationForm(request.POST,request.FILES)
        context['move_manager_form'] = add_move_manager_form
        if add_move_manager_form.is_valid():
            first_name = add_move_manager_form.cleaned_data['first_name']
            last_name = add_move_manager_form.cleaned_data['last_name']
            middle_name = add_move_manager_form.cleaned_data['middle_name']
            gender = add_move_manager_form.cleaned_data['gender']
            address = add_move_manager_form.cleaned_data['address']
            city = add_move_manager_form.cleaned_data['city']
            state = add_move_manager_form.cleaned_data['state']
            zip_code = add_move_manager_form.cleaned_data['zip_code']
            date_of_birth = add_move_manager_form.cleaned_data['date_of_birth']
            phone_number = add_move_manager_form.cleaned_data['phone_number']
            email = add_move_manager_form.cleaned_data['email']
            profile_picture = add_move_manager_form.cleaned_data['profile_picture']
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
                    new_move_manager = MoveManager(user = new_user,
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
                    new_move_manager.save()
                    #Save Image
                    new_move_manager.profile_picture = profile_picture
                    new_move_manager.save()
                    #Add new user to UserRoles with CAREGIVER Role
                    new_role = UserRoles(company=company,
                                            user=new_user,
                                            role='MOVEMANAGER')
                    new_role.save()
                    #Send verification email
                    current_site = get_current_site(request)
                    email_manager = MoveManagerEmailProcessor()
                    email_manager.send_verification_email(
                    new_user, current_site.domain
                    )
                    #Add messages
                    messages.success(request, "Move Manager {0} {1} successfully added!".format(first_name, last_name))
                    return redirect('add_move_manager')
            except IntegrityError as e:
                messages.error(request, "Move manager has already been registered. Please enter with a new email address.")
        else:
            form_errors = add_move_manager_form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
        return render(request, 'production/add_move_manager.html', context)

class EditChooseMoveManager(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_move_managers = MoveManager.objects.filter(company=current_company).order_by('last_name')
        context['all_move_managers'] = all_move_managers
        context['find_move_manager_form'] = FindMoveManagerForm()
        return render(request, 'production/choose_edit_move_manager.html', context)

    def post(self, request):
        #Not really necessary - doesn't do anything right now
        context = {}
        return render(request, 'production/choose_edit_move_manager.html', context)

class EditMoveManager(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        find_move_manager_form = FindMoveManagerForm(request.GET)
        current_company = request.user.company
        if find_move_manager_form.is_valid():
            move_manager_email = find_move_manager_form.cleaned_data['move_manager_email']
            move_manager = MoveManager.objects.get(company=current_company,email_address=move_manager_email)
            move_manager_birthday = self.parse_date(move_manager.date_of_birth)
            edit_move_manager_form = MoveManagerEditForm(initial=
            {
                'first_name': move_manager.first_name,
                'last_name': move_manager.last_name,
                'middle_name': move_manager.middle_name,
                'gender': move_manager.gender,
                'address': move_manager.address,
                'city': move_manager.city,
                'state': move_manager.state,
                'zip_code': move_manager.zip_code,
                'date_of_birth': move_manager_birthday,
                'phone_number': move_manager.phone_number,
                'email': move_manager.email_address,
                'profile_picture': move_manager.profile_picture,
            })
            context['edit_move_manager_form'] = edit_move_manager_form
        else:
            form_errors = find_move_manager_form.errors.as_data()
            error_messaging.render_error_messages(request, form_errors)
        return render(request, 'production/edit_move_manager.html', context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_move_manager_form = MoveManagerEditForm(request.POST,request.FILES)
        email = request.POST.get('email')
        context['edit_move_manager_form'] = edit_move_manager_form
        if edit_move_manager_form.is_valid():
            try:
                first_name = edit_move_manager_form.cleaned_data['first_name']
                last_name = edit_move_manager_form.cleaned_data['last_name']
                middle_name = edit_move_manager_form.cleaned_data['middle_name']
                gender = edit_move_manager_form.cleaned_data['gender']
                address = edit_move_manager_form.cleaned_data['address']
                city = edit_move_manager_form.cleaned_data['city']
                state = edit_move_manager_form.cleaned_data['state']
                zip_code = edit_move_manager_form.cleaned_data['zip_code']
                date_of_birth = edit_move_manager_form.cleaned_data['date_of_birth']
                phone_number = edit_move_manager_form.cleaned_data['phone_number']
                email = edit_move_manager_form.cleaned_data['email']
                profile_picture = edit_move_manager_form.cleaned_data['profile_picture']
                #Get current
                move_manager = MoveManager.objects.get(company=current_company,email_address=email)
                move_manager.first_name = first_name
                move_manager.last_name = last_name
                move_manager.middle_name = middle_name
                move_manager.gender = gender
                move_manager.address = address
                move_manager.city = city
                move_manager.state = state
                move_manager.zip_code = zip_code
                move_manager.date_of_birth = date_of_birth
                move_manager.phone_number = phone_number
                if profile_picture != None and move_manager.profile_picture != profile_picture:
                    move_manager.profile_picture = profile_picture
                if move_manager.email_address != None and move_manager.email_address != email:
                    move_manager.email_address = email
                    move_manager_auth = User.objects.get(company=current_company,email=email)
                    move_manager_auth.email = email
                    move_manager_auth.save()
                move_manager.save()
                print("SAVED MM")
                messages.success(request, "Move Manager {0} {1} successfully edited!".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Move Manager already exists. Please add a new Move Manager")
        return HttpResponseRedirect(reverse('edit_move_manager') + "?move_manager_email=" + email)

    def parse_date(self,caregiver_birthday):
        caregiver_birthday = caregiver_birthday.date()
        output_month = caregiver_birthday.month
        output_day = caregiver_birthday.day
        output_year = caregiver_birthday.year
        output_string = "{0}/{1}/{2}".format(output_month,output_day,output_year)
        return output_string

class MoveManageWizard(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['create_move_task_form'] = CreateMoveTaskForm()
        return render(request, "production/move_management_wizard.html", context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        create_move_task_form = CreateMoveTaskForm(request.POST)
        if create_move_task_form.is_valid():
            client_uid = create_move_task_form.cleaned_data['client_uid']
            new_address_max_distance = create_move_task_form.cleaned_data['new_address_max_distance']
            type_of_home = create_move_task_form.cleaned_data['type_of_home']
            provides_assistance = create_move_task_form.cleaned_data['provides_assistance']
            minimum_cost = create_move_task_form.cleaned_data['minimum_cost']
            maximum_cost = create_move_task_form.cleaned_data['maximum_cost']
            type_of_area = create_move_task_form.cleaned_data['type_of_area']
            handicap_friendly = create_move_task_form.cleaned_data['handicap_friendly']
            furnished = create_move_task_form.cleaned_data['furnished']

            client = Client.objects.get(company=current_company, uid = client_uid)
            print(client)

            move_task = MoveManageTask(company=current_company,
                                        client=client,
                                        address=client.address,
                                        city=client.city,
                                        state=client.state,
                                        zip_code=client.zip_code,
                                        new_address_max_distance=new_address_max_distance,
                                        type_of_home=type_of_home,
                                        provides_assistance=provides_assistance,
                                        minimum_cost=minimum_cost,
                                        maximum_cost=maximum_cost,
                                        type_of_area=type_of_area,
                                        handicap_friendly=handicap_friendly,
                                        furnished=furnished)
            move_task.save()
            messages.success(request, "Created relocation task")
        else:
            print(create_move_task_form.errors)
            messages.error(request, "Error creating relocation task")
        return redirect('home_dashboard')

class ChooseMoveContractorForTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid=task_id)
        all_move_managers = MoveManager.objects.filter(company=current_company).order_by('last_name')

        context['all_move_managers'] = all_move_managers
        context['task_id'] = task_id
        context['task'] = task
        return render(request, "production/move_management_tables.html", context)

    def post(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        move_manager_id = self.kwargs['manager_id']
        task = MoveManageTask.objects.get(company=current_company, uid=task_id)
        move_manager = MoveManager.objects.get(company=current_company, uid=move_manager_id)
        task.chosen_manager.add(move_manager)
        task.save()
        return redirect('choose_move_contractor', task_id=task_id)

class MoveInventory(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid=task_id)
        inventory = MoveManageTaskInventory.objects.filter(company=current_company,move_manage_task=task)
        context['inventory'] = inventory
        context['move_task'] = task
        context['add_move_inventory_form'] = AddMoveInventoryForm()
        return render(request, "production/move_inventory.html", context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        add_move_inventory_form = AddMoveInventoryForm(request.POST)
        move_task_uid = request.POST['move_task_uid']
        if add_move_inventory_form.is_valid():
            item = add_move_inventory_form.cleaned_data['item']
            item_quantity = add_move_inventory_form.cleaned_data['item_quantity']
            move_task_uid = add_move_inventory_form.cleaned_data['move_task_uid']
            move_task = MoveManageTask.objects.get(company=current_company, uid=move_task_uid)
            inventory = MoveManageTaskInventory(company=current_company,
                                                move_manage_task=move_task,
                                                item=item,
                                                item_quantity=item_quantity)
            inventory.save()
            messages.success(request, "Added item {0} to inventory".format(item))
        else:
            messages.error(request, "Error adding item to inventory")
        return redirect("move_inventory", task_id=move_task_uid)

@login_required
def get_move_manager_with_email(request):
    if request.method == 'GET':
        context = {}
        email = request.GET.get('email_data')
        current_company = request.user.company
        move_manager = MoveManager.objects.get(company=current_company,email_address = email)
        name = '{0} {1}'.format(move_manager.first_name, move_manager.last_name)
        address = '{0}, {1} {2} {3}'.format(move_manager.address, move_manager.city, move_manager.state, move_manager.zip_code)
        phone_number = move_manager.phone_number
        raw_dob = move_manager.date_of_birth
        date_of_birth = '{0}/{1}/{2}'.format(raw_dob.month,raw_dob.day,raw_dob.year)
        gender = move_manager.gender
        move_manager_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'date_of_birth': date_of_birth,
                        'gender': gender,
                        'email_address': email}
        if move_manager.profile_picture:
            move_manager_data['profile_picture'] = move_manager.profile_picture.url
        context["move_manager_data"] = move_manager_data
        #return JsonResponse(caregiver_data)
        return HttpResponse(json.dumps(move_manager_data), content_type="application/json")
