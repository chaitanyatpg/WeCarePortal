from django.shortcuts import render
from django.http import HttpResponse, request
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
            other_state_name = add_home_mod_manager_form.cleaned_data['other_state_name']
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
                    messages.success(request, "Home modification manager {0} {1} added successfully.".format(first_name, last_name))
                    return redirect('add_home_mod_manager')
            except IntegrityError as e:
                messages.error(request, "Home modification user has already been registered. Please enter with a new email address.")
        else:
            form_errors = add_home_mod_manager_form.errors.as_data()
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
                other_state_name = edit_home_mod_user_form.cleaned_data['other_state_name']
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
                if home_mod_user.state == "Other":
                    home_mod_user.state = other_state_name

                if profile_picture != None and home_mod_user.profile_picture != profile_picture:
                    home_mod_user.profile_picture = profile_picture
                if home_mod_user.email_address != None and home_mod_user.email_address != email:
                    home_mod_user.email_address = email
                    home_mod_user_auth = User.objects.get(company=current_company,email=email)
                    home_mod_user_auth.email = email
                    home_mod_user_auth.save()
                home_mod_user.save()
                print("SAVED HMU")
                messages.success(request, "Home modification manager {0} {1} edited successfully.".format(first_name,last_name))
            except IntegrityError as e:
                messages.error(request, "Home modification manager already exists. Please add a new Home Modification Manager")
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
        current_company = request.user.company
        home_mod_user = HomeModificationUser.objects.get(company=current_company,
                                                        user=request.user)
        contractor_tasks = HomeModificationTask.objects.filter(company=current_company,chosen_contractors=home_mod_user).order_by('-created')
        home_mod_task_bids = HomeModTaskBid.objects.filter(company=current_company,contractor=home_mod_user)

        context['home_mod_task_bids'] = home_mod_task_bids
        context['home_mod_user'] = home_mod_user
        context['contractor_tasks'] = contractor_tasks
        context['bid_form'] = BidForm()
        return render(request, 'production/contractor_dashboard.html', context)

    def post(self, request):

        context = {}
        current_company = request.user.company
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            task_uid = bid_form.cleaned_data['task_uid']
            start_date = bid_form.cleaned_data['start_date']
            end_date = bid_form.cleaned_data['end_date']
            cost = bid_form.cleaned_data['cost']
            contractor = HomeModificationUser.objects.get(company=current_company,
                                                            user=request.user)
            home_mod_task = HomeModificationTask.objects.get(company=current_company,
                                                            uid=task_uid)
            home_mod_task_bid = HomeModTaskBid(company=current_company,
                                            home_mod_task=home_mod_task,
                                            contractor=contractor,
                                            start_date = start_date,
                                            end_date = end_date,
                                            cost = cost)
            home_mod_task_bid.save()
            messages.success(request, "Bid sent.")
        else:
            messages.error(request, "Error sending bid")
        return redirect('contractor_dashboard')

class ViewBids(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        context={}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = HomeModificationTask.objects.get(company=current_company, uid=task_id)
        bids = HomeModTaskBid.objects.filter(company=current_company, home_mod_task=task)
        context['task'] = task
        context['task_id'] = task_id
        context['bids'] = bids
        return render(request, "production/view_bids.html", context)

class ModifyBid(LoginRequiredMixin, View):

    def post(self, request):
        return redirect('view_bids')

class AcceptBid(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context={}
        current_company = request.user.company
        bid_id = request.POST['bid_id']
        if HomeModTaskBid.objects.filter(company=current_company, uid=bid_id,bid_live= True).exists():
            bid = HomeModTaskBid.objects.get(company=current_company, uid=bid_id)
            task = bid.home_mod_task
            # Set chosen bid of the task
            task.chosen_bid = bid
            task.save()
            # Create new Home Mod project
            if not HomeModProject.objects.filter(company=current_company,home_mod_task = task).exists():
                home_mod_project = HomeModProject(company=current_company,home_mod_task = task,estimated_budget = bid.cost,contractor = bid.contractor,client = task.client)
                home_mod_project.save()
                messages.success(request, "Accepted bid from {0} {1} for task {2} and created project".format(bid.contractor.first_name, bid.contractor.last_name, task.task_name))
            else:
                messages.success(request,"Bid already accepted")
        else:
            messages.success(request, "Bid doesn't exist") 
        return redirect('home_dashboard')

class UpdateProjects(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        home_mod_user = HomeModificationUser.objects.get(company=current_company,
                                                        user=request.user)
        projects = HomeModProject.objects.filter(company=current_company, contractor=home_mod_user, home_mod_task__archived=False)
        context['projects'] = projects
        return render(request, "production/update_projects.html", context)

class ViewProject(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        home_mod_project_id = self.kwargs['home_mod_project_id']
        home_mod_project = HomeModProject.objects.get(company = current_company,
                                                    uid = home_mod_project_id)
        context['project'] = home_mod_project
        (progress_list, budget_list, amount_spent_list,
            duration_list, status_list) = self.get_graph_series(home_mod_project, current_company)

        context['progress_list'] = [x.progress for x in progress_list]
        context['progress_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in progress_list]

        context['amount_spent_list'] = [x.total_amount_spent for x in amount_spent_list]
        context['amount_spent_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in amount_spent_list]

        context['budget_list'] = [x.estimated_budget for x in budget_list]
        context['budget_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in budget_list]

        context['duration_list'] = [x.project_duration for x in duration_list]
        context['duration_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in duration_list]

        return render(request, "production/project_view.html", context)

    def get_graph_series(self, home_mod_project, current_company):

        progress_list = HomeModProjectProgressLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        budget_list = HomeModProjectBudgetLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        amount_spent_list = HomeModProjectAmountSpentLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        duration_list = HomeModProjectDurationLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        status_list = HomeModProjectStatusLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')

        return (progress_list, budget_list, amount_spent_list, duration_list, status_list)


class ViewProjectDisabled(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = HomeModificationTask.objects.get(company=current_company, uid = task_id)
        home_mod_project = HomeModProject.objects.get(company = current_company,
                                                    home_mod_task=task)
        context['project'] = home_mod_project
        (progress_list, budget_list, amount_spent_list,
            duration_list, status_list) = self.get_graph_series(home_mod_project, current_company)

        context['progress_list'] = [x.progress for x in progress_list]
        context['progress_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in progress_list]

        context['amount_spent_list'] = [x.total_amount_spent for x in amount_spent_list]
        context['amount_spent_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in amount_spent_list]

        context['budget_list'] = [x.estimated_budget for x in budget_list]
        context['budget_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in budget_list]

        context['duration_list'] = [x.project_duration for x in duration_list]
        context['duration_x_list'] = [x.created.strftime("%Y-%m-%d %H:%M:%S") for x in duration_list]
        return render(request, "production/project_view.html", context)

    def get_graph_series(self, home_mod_project, current_company):

        progress_list = HomeModProjectProgressLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        budget_list = HomeModProjectBudgetLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        amount_spent_list = HomeModProjectAmountSpentLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        duration_list = HomeModProjectDurationLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')
        status_list = HomeModProjectStatusLog.objects.filter(company=current_company, home_mod_project=home_mod_project).order_by('created')

        return (progress_list, budget_list, amount_spent_list, duration_list, status_list)

class DeleteHomeModTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        current_company = request.user.company
        task_id = self.kwargs['task_id']
        task = HomeModificationTask.objects.get(company=current_company, uid = task_id)
        task.delete()
        messages.success(request, "Deleted home modification task")
        return redirect('home_dashboard')

class ArchiveProject(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        task_id = self.kwargs['task_id']
        task = HomeModificationTask.objects.get(company=company, uid=task_id)
        task.archived = True
        task.save()
        messages.success(request, "Closed home modification project")
        return redirect('home_dashboard')

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

# AJAX FUNCTIONS BELOW HERE

@login_required
@transaction.atomic
def save_project_budget(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        budget = request.POST.get('budget')
        project_id = request.POST.get('project_id')
        if budget and project_id:
            project = HomeModProject.objects.get(company = company, uid = project_id)
            project.estimated_budget = budget
            project.save()
            home_mod_budget_log = HomeModProjectBudgetLog(company=company,
                                                            home_mod_project = project,
                                                            estimated_budget = budget)
            home_mod_budget_log.save()
            return HttpResponse("Saved budget")
        else:
            return HttpResponse("Please enter budget amount")

@login_required
@transaction.atomic
def save_project_total_amount_spent(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        total_amount_spent = request.POST.get('total_amount_spent')
        project_id = request.POST.get('project_id')
        if total_amount_spent and project_id:
            project = HomeModProject.objects.get(company = company, uid = project_id)
            project.total_amount_spent = total_amount_spent
            project.save()
            home_mod_amount_spent_log = HomeModProjectAmountSpentLog(company=company,
                                        home_mod_project = project,
                                        total_amount_spent = total_amount_spent)
            home_mod_amount_spent_log.save()
            return HttpResponse("Saved total amount spent")
        else:
            return HttpResponse("Please enter total amount spent")

@login_required
@transaction.atomic
def save_project_duration(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        project_duration = request.POST.get('project_duration')
        project_id = request.POST.get('project_id')
        if project_duration and project_id:
            project = HomeModProject.objects.get(company = company, uid = project_id)
            project.project_duration = project_duration
            project.save()
            home_mod_project_duration = HomeModProjectDurationLog(company=company,
                                        home_mod_project = project,
                                        project_duration = project_duration)
            home_mod_project_duration.save()
            return HttpResponse("Saved project duration")
        else:
            return HttpResponse("Please enter project duration")

@login_required
@transaction.atomic
def save_progress(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        progress = request.POST.get('project_progress')
        project_id = request.POST.get('project_id')
        if progress and project_id:
            project = HomeModProject.objects.get(company = company, uid = project_id)
            project.progress = progress
            project.save()
            home_mod_project_progress = HomeModProjectProgressLog(company=company,
                                        home_mod_project = project,
                                        progress = progress)
            home_mod_project_progress.save()
            return HttpResponse("Saved progress")
        else:
            return HttpResponse("Please enter progress")

@login_required
@transaction.atomic
def save_status(request):

    if request.method == "POST":
        context = {}
        company = request.user.company
        status = request.POST.get('project_status')
        project_id = request.POST.get('project_id')
        if status and project_id:
            project = HomeModProject.objects.get(company = company, uid = project_id)
            project.status = status
            project.save()
            home_mod_project_status = HomeModProjectStatusLog(company = company,
                                        home_mod_project = project,
                                        status = status)
            home_mod_project_status.save()
            return HttpResponse("Saved status")
        else:
            return HttpResponse("Please enter status")



class RejectBid(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        context={}
        current_company = request.user.company
        bid_id = request.POST['bid_id']
        taskbid = HomeModTaskBid.objects.get(company=current_company, uid=bid_id)
        task_id = taskbid.home_mod_task.uid
        if HomeModTaskBid.objects.filter(company=current_company, uid=bid_id,bid_live= True).exists():
            bid = HomeModTaskBid.objects.get(company=current_company, uid=bid_id,bid_live = True)
            
            task = bid.home_mod_task
        # Set chosen bid of the task
            if task.chosen_bid:
                messages.success(request, "Bid already accepted".format(bid.contractor.first_name, bid.contractor.last_name))
            else:
                bid.bid_live = False
                bid.save()
                messages.success(request, "Bid rejected")
        
        else:
            messages.success(request, "Bid doesn't exist")

        # task.save()
        # Create new Home Mod project
        # return redirect('home_dashboard')
        return redirect('view_bids', task_id=task_id)
        # return HttpResponseRedirect(reverse('view_bids', "/"+ task_id))

@login_required
def reject_contractor_bid_task(request):
    if request.method == "POST":
        context = {}
        current_company = request.user.company
        bid_id =  request.POST['bid_id']
        
        if HomeModificationTask.objects.filter(company=current_company, uid=bid_id).exists():
            home_mod_task = HomeModificationTask.objects.get(company=current_company, uid=bid_id)
            # contractor = HomeModificationUser.objects.get(company=current_company,user=request.user)
            
            for contractor in home_mod_task.chosen_contractors.all():
                if contractor.email_address == request.user.email:
                    if ContractorRejectTask.objects.filter(company=current_company,contractor=contractor,home_mod_task= home_mod_task,status = True).exists():
                        messages.success(request, "Reject bid request already sent")
                    else:
                        contractor_reject_task = ContractorRejectTask(company = current_company,contractor=contractor,home_mod_task =home_mod_task,status = True)
                        contractor_reject_task.save()
                        messages.success(request, "Reject bid request sent sucessfully")
                
    return redirect('contractor_dashboard')    
