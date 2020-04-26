from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import redirect
from mycareportal_app.models import *
from mycareportal_app.family_forms import *
from django.views.generic import View
from django.http import JsonResponse
from collections import defaultdict
from dateutil import relativedelta
import datetime
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import pytz
import django.utils.timezone as timezone
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from mycareportal_app.client_forms import *
#  =======================
from mycareportal_app.common import error_messaging as error_messaging
from django.contrib.sites.shortcuts import get_current_site
from mycareportal_app.email.family.family_email_processor import FamilyEmailProcessor
# from mycareportal_app.email.provider.provider_email_processor import ProviderEmailProcessor
# from mycareportal_app.email.legal.legal_email_processor import LegalEmailProcessor
from django.db.models import Q
# ===============
def family_dashboard(request):

    return render(request, 'production/family_dashboard.html')

class FamilyDashboard(LoginRequiredMixin, View):

    MAX_FILE_SIZE = 104857600 #100mb in bytes

    def get(self, request):
        context = {}
        current_company = request.user.company
        family_contact = FamilyContact.objects.get(company=current_company,user=request.user)
        related_clients = Client.objects.filter(company=current_company, family_contacts=family_contact)
        related_caregivers = []
        for client in related_clients:
            client_caregivers = client.caregiver.all()
            related_caregivers += client_caregivers
        context["current_family_contact"] = family_contact
        active_caregivers = self.get_active_caregivers(current_company, related_clients, related_caregivers)
        #active_caregivers = CaregiverTimeSheet.objects.filter(company=current_company, client__in=related_clients, caregiver__in=related_caregivers)
        context['active_caregivers'] = active_caregivers
        context['related_caregivers'] = related_caregivers
        #Get displayable family contact data
        name = '{0} {1}'.format(family_contact.first_name, family_contact.last_name)
        address = '{0}, {1} {2} {3}'.format(family_contact.address, family_contact.city, family_contact.state, family_contact.zip_code)
        phone_number = family_contact.phone_number
        relationship = family_contact.relationship
        family_contact_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'relationship': relationship}
        if family_contact.profile_picture:
            family_contact_data['profile_picture'] = family_contact.profile_picture.url
        context["family_contact_data"] = family_contact_data
        #Get Tasks for related clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        for family_data in related_clients:
            current_client_tasks = self.get_client_tasks(family_data, current_company)
            #client_name = '{0} {1}'.format(family_data.first_name, family_data.last_name)
            client_tasks[family_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        #Get Update Form
        context["update_task_form"] = UpdateTaskForm()

        #For Map of provider and caregiver
        family_member = []
        provider = []
        all_care_giver = []
        for client in related_clients:
            client_family_contacts = client.family_contacts.all()
            family_member =client_family_contacts
            provider = client.provider.all()
            caregiver = client.caregiver.all()
        context["family_member"] = family_member
        context["provider"] = provider
        context["caregiver"] = caregiver
            

        return render(request, 'production/family_dashboard.html', context)

    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST, request.FILES)
        attachments = request.FILES.getlist('attachment')
        are_attachments_valid = self.validate_attachments(request,attachments)
        if are_attachments_valid:
            if update_task_form.is_valid():
                current_company = request.user.company
                comment = update_task_form.cleaned_data["comment"]
                task_id = update_task_form.cleaned_data["task_id"]
                client_id = update_task_form.cleaned_data["client_id"]
                sign_off = update_task_form.cleaned_data["sign_off"]
                client = Client.objects.get(company=current_company,id=client_id)
                task = TaskSchedule.objects.get(company=current_company,client=client,id=task_id)
                # status = update_task_form.cleaned_data["status"]
                self.save_task_comments(request, update_task_form, task, current_company, client, comment)
                self.save_task_attachments(request, update_task_form, task, current_company, client, request.user, attachments)
                if sign_off != task.marked_off:
                    task.mark_off(request.user)
                messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return redirect('family_dashboard')

    def validate_attachments(self, request, attachments):
        for attachment in attachments:
            if attachment._size > self.MAX_FILE_SIZE:
                messages.error(request, "Attachment {0} is too large. All attachments must be under 100mb.".format(attachment))
                return False
        return True

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


    def get_client_tasks(self, family_data, current_company):
        client_timezone = pytz.timezone(family_data.time_zone)
        current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        timezone.activate(client_timezone)
        client_tasks = TaskSchedule.objects.filter(company=current_company,client=family_data,date=current_date).order_by('cancelled','pending','in_progress','complete')
        client_tasks = list(map(lambda x: (x,
        TaskComment.objects.filter(company=current_company,client=family_data,task_schedule=x).order_by('created'),
        # new  for file upload
        TaskAttachment.objects.filter(company=current_company,client=family_data,task_schedule=x).order_by('created'),
        # new  for file upload
        TaskLink.objects.filter(company=current_company,client=family_data,task_schedule=x).order_by('created')),client_tasks))
        return client_tasks

        # new  for file upload

    def save_task_attachments(self, request, update_task_form, task, current_company, client, user, attachments):
        for uploaded_file in attachments:
            task_attachment = TaskAttachment(company=current_company,
                                            client=client,
                                            user=user,
                                            task_schedule=task,
                                            attachment=uploaded_file)
            task_attachment.save()

       # new  for file upload

    def save_task_comments(self, request, update_task_form, task, current_company, client, comment):

        #caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        task_comment = TaskComment(company=current_company,
                                    client=client,
                                    user=request.user,
                                    task_schedule=task,
                                    comment=comment)
        if comment != "":
            task_comment.save()

    def get_active_familymember(self, current_company, related_clients, related_familymember):
        client_timezone = pytz.timezone(related_clients[0].time_zone)
        current_date_time = timezone.now().astimezone(client_timezone)
        active_familymember = FamilyContact.objects.filter(company=current_company,
                    client__in=related_clients,
                    familymember__in=related_familymember,
                    clock_in_timestamp__year=current_date_time.year,
                    clock_in_timestamp__month=current_date_time.month,
                    clock_in_timestamp__day=current_date_time.day)
        return active_familymember




def client_signoff_all(request, client_uid):
    company = request.user.company
    client = Client.objects.get(company=company, uid=client_uid)
    tasks = TaskSchedule.get_todays_tasks(company, client)
    for task in tasks:
        task.mark_off(request.user)
    messages.success(request, "Signed off all tasks")
    return redirect('family_dashboard')


# new family member ==============================
class ChooseClientForLegalMail(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        family_contact = FamilyContact.objects.get(company=current_company,user=request.user)
        related_clients = Client.objects.filter(company=current_company, family_contacts=family_contact)
        familymember = []
        for client in related_clients:
            client_family_contacts = client.family_contacts.all()
            familymember =client_family_contacts
        # context['add_client_form'] = ClientRegistrationForm()
        # client = Client.objects.filter(company = current_company)
        # family_member = FamilyContact.objects.filter(company=current_company,client =client )
        context['family_member'] = familymember
        context['find_family_contact_form'] = FindFamilyContactForm()
        return render(request, 'production/family_email.html', context)

class LegalEmailFamily(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        find_family_contact_form = FindFamilyContactForm(request.GET)
        context['all_timezones'] = pytz.all_timezones
        if find_family_contact_form.is_valid():
            family_email = find_family_contact_form.cleaned_data['family_email']
            familycontact = FamilyContact.objects.get(company=current_company, email_address=family_email)
            context['legal_email_family_form'] = LegalEmailFamilyForm()
            context['familycontact'] = familycontact
            return render(request, 'production/send_family_email.html', context)
        else:
            return redirect('choose_client_for_legal_mail')

    def post(self, request):
        context = {}
        current_company = request.user.company
        legal_email_family_form = LegalEmailFamilyForm(request.POST)

        if legal_email_family_form.is_valid():
            familycontact_uid = legal_email_family_form.cleaned_data['familycontact_uid']
            familycontact = FamilyContact.objects.get(company=current_company,uid=familycontact_uid)
            subject = legal_email_family_form.cleaned_data['subject']
            content = legal_email_family_form.cleaned_data['content']

            current_site = get_current_site(request)
            email_manager = FamilyEmailProcessor()
            email_manager.send_family_email(
                familycontact, subject, content, request.user, current_company
            )
            messages.success(request, "Successfully sent email to legal team. You will be contacted shortly with further details.")
        else:
            messages.error(request, "Error sending email: Please contact customer support")
        return HttpResponseRedirect(reverse('legal_email_family') + "?family_email=" + familycontact.email_address)

@login_required
def get_family_with_email(request):
    if request.method == 'GET':
        context = {}
        email = request.GET.get('email_data')
        current_company = request.user.company
        client = FamilyContact.objects.get(company=current_company,email_address = email)
        name = '{0} {1}'.format(client.first_name, client.last_name)
        address = '{0}, {1} {2} {3}'.format(client.address, client.city, client.state, client.zip_code)
        phone_number = client.phone_number
        family_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'email_address': email}
        if client.profile_picture:
            family_data['profile_picture'] = client.profile_picture.url
        context["family_data"] = family_data
        return HttpResponse(json.dumps(family_data), content_type="application/json")


# new family member ==============================


    
     