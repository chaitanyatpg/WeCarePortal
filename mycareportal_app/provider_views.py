from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from django.core.urlresolvers import reverse
from django.core import serializers
from django.shortcuts import redirect
from mycareportal_app.models import *
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

def provider_dashboard(request):
    return render(request, 'production/provider_portal.html')

class ProviderDashboard(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        provider = Provider.objects.get(company=current_company,user=request.user)
        related_clients = Client.objects.filter(company=current_company, provider=provider)
        related_caregivers = []
        for client in related_clients:
            client_caregivers = client.caregiver.all()
            related_caregivers += client_caregivers
        context["current_provider"] = provider
        active_caregivers = CaregiverTimeSheet.objects.filter(company=current_company, client__in=related_clients, caregiver__in=related_caregivers, is_active=True)
        context['active_caregivers'] = active_caregivers
        #Get displayable family contact data
        #Get Tasks for related clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        for client_data in related_clients:
            current_client_tasks = self.get_client_tasks(client_data, current_company)
            #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
            client_tasks[client_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        #Get Update Form
        #context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/provider_dashboard_2.html', context)

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
