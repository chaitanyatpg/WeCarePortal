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

class MoveManagerDashboard(LoginRequiredMixin, View):

    def get(self, request):

        context = {}
        current_company = request.user.company
        move_manage_user = MoveManager.objects.get(company=current_company,
                                                        user=request.user)
        move_manage_tasks = MoveManageTask.objects.filter(company=current_company,
                                                            chosen_manager=move_manage_user).order_by('-created')
        move_manage_task_bids = MoveManageTaskBid.objects.filter(company=current_company,move_manager=move_manage_user)
        context['move_manage_task_bids'] = move_manage_task_bids
        context['move_manage_user'] = move_manage_user
        context['move_manage_tasks'] = move_manage_tasks
        context['bid_form'] = BidForm()
        return render(request, 'production/move_manager_main_dashboard.html', context)

    def post(self, request):

        context = {}
        current_company = request.user.company
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            task_uid = bid_form.cleaned_data['task_uid']
            start_date = bid_form.cleaned_data['start_date']
            end_date = bid_form.cleaned_data['end_date']
            cost = bid_form.cleaned_data['cost']
            contractor = MoveManager.objects.get(company=current_company,
                                                            user=request.user)
            move_manage_task = MoveManageTask.objects.get(company=current_company,
                                                            uid=task_uid)
            move_manage_task_bid = MoveManageTaskBid(company=current_company,
                                            move_manage_task=move_manage_task,
                                            move_manager=contractor,
                                            start_date = start_date,
                                            end_date = end_date,
                                            cost = cost)
            move_manage_task_bid.save()
            messages.success(request, "Bid sent.")
        else:
            messages.error(request, "Error sending bid")
        return redirect('move_manager_dashboard')

class ViewMoveBids(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        context={}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid=task_id)
        bids = MoveManageTaskBid.objects.filter(company=current_company, move_manage_task=task)
        context['task'] = task
        context['task_id'] = task_id
        context['bids'] = bids
        return render(request, "production/view_move_bids.html", context)

class AcceptMoveBid(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context={}
        current_company = request.user.company
        bid_id =  request.POST['bid_id']
        if MoveManageTaskBid.objects.filter(company=current_company, uid=bid_id,bid_live = True).exists():
            bid = MoveManageTaskBid.objects.get(company=current_company, uid=bid_id,bid_live = True)
            task = bid.move_manage_task
            # Set chosen bid of the task
            task.chosen_bid = bid
            task.save()
            # Create new Move Management project
            if not MoveManagementProject.objects.filter(company=current_company,move_manage_task = task).exists():
                move_manage_project = MoveManagementProject(company=current_company,move_manage_task = task,estimated_budget = bid.cost,move_manager = bid.move_manager,client = task.client)
                move_manage_project.save()
                messages.success(request, "Accepted bid from {0} {1} and created move management project".format(bid.move_manager.first_name, bid.move_manager.last_name))
            else:
                messages.success(request,"Bid already accepted")

            
        else:
            messages.success(request, "Bid doesn't exist")
        return redirect('home_dashboard')

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
            other_state_name = add_move_manager_form.cleaned_data['other_state_name']
            company = request.user.company
            #Create home mod user auth model and save
            try:
                with transaction.atomic():
                    if state == "Other":
                        state = other_state_name
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
                    messages.success(request, "Move manager {0} {1} added successfully.".format(first_name, last_name))
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
                other_state_name = edit_move_manager_form.cleaned_data['other_state_name']
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
                if move_manager.state == "Other":
                    move_manager.state = other_state_name

                
                if profile_picture != None and move_manager.profile_picture != profile_picture:
                    move_manager.profile_picture = profile_picture
                if move_manager.email_address != None and move_manager.email_address != email:
                    move_manager.email_address = email
                    move_manager_auth = User.objects.get(company=current_company,email=email)
                    move_manager_auth.email = email
                    move_manager_auth.save()
                move_manager.save()
                print("SAVED MM")
                messages.success(request, "Move manager {0} {1} edited successfully.".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Move manager already exists. Please add a new Move Manager")
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
            messages.error(request, "Error creating relocation task")
        return redirect('home_dashboard')

class ChooseMoveContractorForTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid=task_id)
        all_move_managers = MoveManager.objects.filter(company=current_company).order_by('last_name')

        context['assign_move_manager_form'] = AssignMoveManagerForm()
        context['all_move_managers'] = all_move_managers
        context['task_id'] = task_id
        context['task'] = task
        return render(request, "production/move_management_tables.html", context)

    def post(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        # task_id = self.kwargs['task_id']
        # move_manager_id = self.kwargs['manager_id']
        assign_move_manager_form = AssignMoveManagerForm(request.POST)
        if assign_move_manager_form.is_valid():
            move_manager_email = assign_move_manager_form.cleaned_data['move_manager_email']
            taskuid = assign_move_manager_form.cleaned_data['taskuid']
            is_unassign = assign_move_manager_form.cleaned_data['is_unassign']
            
            task = MoveManageTask.objects.get(company=current_company, uid=taskuid)
            move_manager = MoveManager.objects.get(company=current_company, email_address =move_manager_email)
            
            if is_unassign == "True":
                task.chosen_manager.remove(move_manager)
                bids = MoveManageTaskBid.objects.filter(company = current_company,move_manage_task =task,move_manager =move_manager)
                for i in bids:
                    bids = MoveManageTaskBid.objects.get(id = i.id)
                    bids.archived =  True
                    bids.save()
                if MoveManagerRejectTask.objects.filter(company=current_company,move_manager=move_manager,move_manage_task= task,status = True).exists():
                    manager_reject_task = MoveManagerRejectTask.objects.get(company = current_company,move_manager =move_manager, move_manage_task = task,status = True)
                    manager_reject_task.status = False
                    manager_reject_task.save()
            else:
                task.chosen_manager.add(move_manager)
                if MoveManageTaskBid.objects.filter(company = current_company,move_manage_task =task,move_manager =move_manager).exists():
                    bids = MoveManageTaskBid.objects.filter(company = current_company,move_manage_task =task,move_manager =move_manager)
                    for i in bids:
                        bids = MoveManageTaskBid.objects.get(id = i.id)
                        bids.archived =  False
                        bids.save()


            task.save()

            # task = MoveManageTask.objects.get(company=current_company, uid=task_id)
            # move_manager = MoveManager.objects.get(company=current_company, uid=move_manager_id)
       
        return redirect('choose_move_contractor', task_id=taskuid)

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
        add_move_inventory_form = AddMoveInventoryForm(request.POST, request.FILES)
        move_task_uid = request.POST['move_task_uid']
        if add_move_inventory_form.is_valid():
            item = add_move_inventory_form.cleaned_data['item']
            item_quantity = add_move_inventory_form.cleaned_data['item_quantity']
            item_price = add_move_inventory_form.cleaned_data['item_price']
            item_destination = add_move_inventory_form.cleaned_data['item_destination']
            item_image = add_move_inventory_form.cleaned_data['item_image']
            move_task_uid = add_move_inventory_form.cleaned_data['move_task_uid']
            move_task = MoveManageTask.objects.get(company=current_company, uid=move_task_uid)
            inventory = MoveManageTaskInventory(company=current_company,
                                                move_manage_task=move_task,
                                                item=item,
                                                item_quantity=item_quantity,
                                                item_price = item_price,
                                                item_destination = item_destination)
            inventory.save()
            # Add Image
            inventory.item_image = item_image
            inventory.save()
            messages.success(request, "Added item {0} to inventory".format(item))
        else:
            messages.error(request, "Error adding item to inventory")
        return redirect("move_inventory", task_id=move_task_uid)

class EditMoveInventory(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        inventory_id = self.kwargs['inventory_id']
        inventory_item = MoveManageTaskInventory.objects.get(company=current_company, uid=inventory_id)
        edit_inventory_form = EditMoveInventoryForm(initial=
        {
            'inventory_uid': inventory_item.uid,
            'item': inventory_item.item,
            'item_quantity': inventory_item.item_quantity,
            'item_price': inventory_item.item_price,
            'item_sale_price': inventory_item.item_sale_price,
            'item_destination': inventory_item.item_destination,
            'item_sold': inventory_item.item_sold,
            'item_image': inventory_item.item_image,
        })
        context['inventory_item'] = inventory_item
        context['edit_inventory_form'] = edit_inventory_form
        return render(request, "production/edit_move_inventory.html", context)

    def post(self, request):
        context = {}
        current_company = request.user.company
        edit_inventory_form = EditMoveInventoryForm(request.POST, request.FILES)
        if edit_inventory_form.is_valid():
            item = edit_inventory_form.cleaned_data['item']
            item_quantity = edit_inventory_form.cleaned_data['item_quantity']
            item_price = edit_inventory_form.cleaned_data['item_price']
            item_sale_price = edit_inventory_form.cleaned_data['item_sale_price']
            item_destination = edit_inventory_form.cleaned_data['item_destination']
            item_sold = edit_inventory_form.cleaned_data['item_sold']
            inventory_uid = edit_inventory_form.cleaned_data['inventory_uid']
            item_image = edit_inventory_form.cleaned_data['item_image']
            inventory_item = MoveManageTaskInventory.objects.get(company=current_company, uid=inventory_uid)
            inventory_item.item = item
            inventory_item.item_quantity = item_quantity
            inventory_item.item_price = item_price
            inventory_item.item_sale_price = item_sale_price
            inventory_item.item_destination = item_destination
            inventory_item.item_sold = item_sold
            if item_image is not None:
                inventory_item.item_image = item_image
            inventory_item.save()
            messages.success(request, "Saved inventory item {0}".format(item))
        else:
            messages.error(request, "Error saving inventory item")
        return redirect('edit_move_inventory', inventory_id=inventory_uid)

class UpdateMoveProjects(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        move_manager = MoveManager.objects.get(company=current_company,
                                                        user=request.user)
        projects = MoveManagementProject.objects.filter(company=current_company,
                                                        move_manager=move_manager,
                                                        move_manage_task__archived=False)
        context['projects'] = projects
        return render(request, "production/update_move_projects.html", context)

class ViewMoveProject(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        move_project_id = self.kwargs['move_project_id']
        move_project = MoveManagementProject.objects.get(company = current_company,
                                                    uid = move_project_id)
        context['project'] = move_project
        (progress_list, budget_list, amount_spent_list,
            duration_list, status_list) = self.get_graph_series(move_project, current_company)

        context['progress_list'] = [x.progress for x in progress_list]
        context['progress_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in progress_list]

        context['amount_spent_list'] = [x.total_amount_spent for x in amount_spent_list]
        context['amount_spent_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in amount_spent_list]

        context['budget_list'] = [x.estimated_budget for x in budget_list]
        context['budget_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in budget_list]

        context['duration_list'] = [x.project_duration for x in duration_list]
        context['duration_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in duration_list]

        return render(request, "production/move_project_view.html", context)

    def get_graph_series(self, move_project, current_company):

        progress_list = MoveProjectProgressLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        budget_list = MoveProjectBudgetLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        amount_spent_list = MoveProjectAmountSpentLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        duration_list = MoveProjectDurationLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        status_list = MoveProjectStatusLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')

        return (progress_list, budget_list, amount_spent_list, duration_list, status_list)

class ViewMoveProjectDisabled(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid = task_id)
        move_project = MoveManagementProject.objects.get(company = current_company,
                                                    move_manage_task=task)
        context['project'] = move_project
        (progress_list, budget_list, amount_spent_list,
            duration_list, status_list) = self.get_graph_series(move_project, current_company)

        context['progress_list'] = [x.progress for x in progress_list]
        context['progress_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in progress_list]

        context['amount_spent_list'] = [x.total_amount_spent for x in amount_spent_list]
        context['amount_spent_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in amount_spent_list]

        context['budget_list'] = [x.estimated_budget for x in budget_list]
        context['budget_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in budget_list]

        context['duration_list'] = [x.project_duration for x in duration_list]
        context['duration_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in duration_list]
        return render(request, "production/move_project_view.html", context)

    def get_graph_series(self, move_project, current_company):

        progress_list = MoveProjectProgressLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        budget_list = MoveProjectBudgetLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        amount_spent_list = MoveProjectAmountSpentLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        duration_list = MoveProjectDurationLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')
        status_list = MoveProjectStatusLog.objects.filter(company=current_company, move_management_project=move_project).order_by('created')

        return (progress_list, budget_list, amount_spent_list, duration_list, status_list)

class DeleteMoveTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=current_company, uid = task_id)
        task.delete()
        messages.success(request, "Deleted move task")
        return redirect('home_dashboard')

class ArchiveProject(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        task_id = self.kwargs['task_id']
        task = MoveManageTask.objects.get(company=company, uid=task_id)
        task.archived = True
        task.save()
        messages.success(request, "Closed move project")
        return redirect('home_dashboard')

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

@login_required
@transaction.atomic
def save_move_project_budget(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        budget = request.POST.get('budget')
        project_id = request.POST.get('project_id')
        if budget and project_id:
            project = MoveManagementProject.objects.get(company = company, uid = project_id)
            project.estimated_budget = budget
            project.save()
            move_budget_log = MoveProjectBudgetLog(company=company,
                                                            move_management_project = project,
                                                            estimated_budget = budget)
            move_budget_log.save()
            return HttpResponse("Saved budget")
        else:
            return HttpResponse("Please enter budget amount")

@login_required
@transaction.atomic
def save_move_project_total_amount_spent(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        total_amount_spent = request.POST.get('total_amount_spent')
        project_id = request.POST.get('project_id')
        if total_amount_spent and project_id:
            project = MoveManagementProject.objects.get(company = company, uid = project_id)
            project.total_amount_spent = total_amount_spent
            project.save()
            move_amount_spent_log = MoveProjectAmountSpentLog(company=company,
                                        move_management_project = project,
                                        total_amount_spent = total_amount_spent)
            move_amount_spent_log.save()
            return HttpResponse("Saved total amount spent")
        else:
            return HttpResponse("Please enter total amount spent")

@login_required
@transaction.atomic
def save_move_project_duration(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        project_duration = request.POST.get('project_duration')
        project_id = request.POST.get('project_id')
        if project_duration and project_id:
            project = MoveManagementProject.objects.get(company = company, uid = project_id)
            project.project_duration = project_duration
            project.save()
            move_project_duration = MoveProjectDurationLog(company=company,
                                        move_management_project = project,
                                        project_duration = project_duration)
            move_project_duration.save()
            return HttpResponse("Saved project duration")
        else:
            return HttpResponse("Please enter project duration")

@login_required
@transaction.atomic
def save_move_progress(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        progress = request.POST.get('project_progress')
        project_id = request.POST.get('project_id')
        if progress and project_id:
            project = MoveManagementProject.objects.get(company = company, uid = project_id)
            project.progress = progress
            project.save()
            move_project_progress = MoveProjectProgressLog(company=company,
                                        move_management_project = project,
                                        progress = progress)
            move_project_progress.save()
            return HttpResponse("Saved progress")
        else:
            return HttpResponse("Please enter progress")

@login_required
@transaction.atomic
def save_move_status(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        status = request.POST.get('project_status')
        project_id = request.POST.get('project_id')
        if status and project_id:
            project = MoveManagementProject.objects.get(company = company, uid = project_id)
            project.status = status
            project.save()
            move_project_status = MoveProjectStatusLog(company = company,
                                        move_management_project = project,
                                        status = status)
            move_project_status.save()
            return HttpResponse("Saved status")
        else:
            return HttpResponse("Please enter status")



class RejectMoveBid(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context={}
        current_company = request.user.company
        bid_id =  request.POST['bid_id']
        taskbid = MoveManageTaskBid.objects.get(company=current_company, uid=bid_id)
        task_id =taskbid.move_manage_task.uid
        if MoveManageTaskBid.objects.filter(company=current_company, uid=bid_id,bid_live = True).exists():
            bid = MoveManageTaskBid.objects.get(company=current_company, uid=bid_id,bid_live = True)
            
            task = bid.move_manage_task
            
        # Set chosen bid of the task
            if task.chosen_bid:
                messages.success(request, "Bid already accepted".format(bid.move_manager.first_name, bid.move_manager.last_name))
            else:
                bid.bid_live = False
                bid.save()
                messages.success(request, "Bid rejected")
         
        else:
            messages.success(request, "Bid doesn't exist")
        return redirect('view_move_bids', task_id=task_id)    
                # delete()
            # messages.success(request, "Reject Bid from {0} {1}".format(bid.move_manager.first_name, bid.move_manager.last_name))
        # task.save()
        # Create new Move Management project
        # move_manage_project = MoveManagementProject(company=current_company,
        #                                     move_manage_task = task,
        #                                     estimated_budget = bid.cost,
        #                                     move_manager = bid.move_manager,
        #                                     client = task.client)
        # move_manage_project.save()
        # return redirect('home_dashboard')
        

@login_required
def reject_mov_manager_bid_task(request):
    if request.method == "POST":
        context = {}
        current_company = request.user.company
        bid_id =  request.POST['bid_id']
        
        
        if MoveManageTask.objects.filter(company=current_company, uid=bid_id).exists():
            move_manage_task = MoveManageTask.objects.get(company=current_company, uid=bid_id)
            
            for move_manager in move_manage_task.chosen_manager.all():
                if move_manager.email_address == request.user.email:
                    if MoveManagerRejectTask.objects.filter(company=current_company,move_manager=move_manager,move_manage_task= move_manage_task,status = True).exists():
                        messages.success(request, "Reject bid request already sent")
                    else:
                        contractor_reject_task = MoveManagerRejectTask(company = current_company,move_manager=move_manager,move_manage_task =move_manage_task,status = True)
                        contractor_reject_task.save()
                        messages.success(request, "Reject bid request sent successfully")
                
    return redirect('move_manager_dashboard')  