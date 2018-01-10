from django.shortcuts import render
from django.http import HttpResponse
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

def family_dashboard(request):

    return render(request, 'production/family_dashboard.html')

class FamilyDashboard(LoginRequiredMixin, View):

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
        active_caregivers = CaregiverTimeSheet.objects.filter(company=current_company, client__in=related_clients, caregiver__in=related_caregivers, is_active=True)
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
        for client_data in related_clients:
            current_client_tasks = self.get_client_tasks(client_data, current_company)
            #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
            client_tasks[client_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        #Get Update Form
        context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/family_dashboard.html', context)

    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST, request.FILES)
        if update_task_form.is_valid():
            current_company = request.user.company
            comment = update_task_form.cleaned_data["comment"]
            task_id = update_task_form.cleaned_data["task_id"]
            client_id = update_task_form.cleaned_data["client_id"]
            client = Client.objects.get(company=current_company,id=client_id)
            task = TaskSchedule.objects.get(company=current_company,client=client,id=task_id)
            self.save_task_comments(request, update_task_form, task, current_company, client, comment)
            messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return redirect('family_dashboard')

    def get_client_tasks(self, client_data, current_company):
        client_timezone = pytz.timezone(client_data.time_zone)
        #current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        timezone.activate(client_timezone)
        client_tasks = TaskSchedule.objects.filter(company=current_company,client=client_data,date=current_date).order_by('cancelled','pending','in_progress','complete')
        client_tasks = list(map(lambda x: (x,
        TaskComment.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created'),
        TaskAttachment.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created'),
        TaskLink.objects.filter(company=current_company,client=client_data,task_schedule=x).order_by('created')),client_tasks))
        return client_tasks

    def save_task_comments(self, request, update_task_form, task, current_company, client, comment):

        #caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        task_comment = TaskComment(company=current_company,
                                    client=client,
                                    user=request.user,
                                    task_schedule=task,
                                    comment=comment)
        if comment != "":
            task_comment.save()
