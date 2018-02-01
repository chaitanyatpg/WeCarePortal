from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db import transaction
from mycareportal_app.models import *
from mycareportal_app.caregiver_forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import View
import datetime
import pytz
import django.utils.timezone as timezone
import json
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

class ViewAllCaregivers(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        caregivers = Caregiver.objects.filter(company=company).order_by('last_name')
        context['caregivers'] = caregivers
        return render(request, "production/view_all_caregivers.html", context)

class ViewAllClients(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        clients = Client.objects.filter(company=company).order_by('last_name')
        context['clients'] = clients
        return render(request, "production/view_all_clients.html", context)

class ViewAllCareManagers(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        company = request.user.company
        care_managers = CareManager.objects.filter(company=company)
        context['care_managers'] = care_managers
        return render(request, "production/view_all_care_managers.html", context)

class ViewClientsWithoutCaregiver(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        print("ASDASDASGGGG")
        company = request.user.company
        clients = Client.objects.filter(company=company,caregiver=None).order_by('last_name')
        context['clients'] = clients
        return render(request, "production/view_all_clients.html", context)

class ViewTasks(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = {}
        task_type = self.kwargs['task_type']
        start_date = timezone.now()
        end_date = timezone.now()
        if 'start_date' in self.kwargs:
            start_date = self.kwargs['start_date']
        if 'end_date' in self.kwargs:
            end_date = self.kwargs['end_date']
        if task_type=="scheduled":
            tasks = TaskSchedule.objects.filter(company=request.user.company,date__range=[start_date,end_date])
        if task_type=="pending":
            tasks = TaskSchedule.objects.filter(company=request.user.company,date__range=[start_date,end_date],pending=True)
        if task_type=="in_progress":
            tasks = TaskSchedule.objects.filter(company=request.user.company,date__range=[start_date,end_date],in_progress=True)
        if task_type=="complete":
            tasks = TaskSchedule.objects.filter(company=request.user.company,date__range=[start_date,end_date],complete=True)
        if task_type=="cancelled":
            tasks = TaskSchedule.objects.filter(company=request.user.company,date__range=[start_date,end_date],cancelled=True)
        if task_type=="default":
            tasks = TaskSchedule.objects.filter(company=request.user.company)
        if task_type=="custom":
            tasks = TaskSchedule.objects.filter(company=request.user.company)
        context['tasks'] = tasks
        return render(request, "production/view_tasks.html", context)
