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
from mycareportal_app.provider_forms import *
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q

def provider_dashboard(request):
    return render(request, 'production/provider_portal.html')

class ProviderDashboard(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        #current_company = request.user.company
        provider = Provider.objects.filter(user=request.user)
        related_clients = Client.objects.filter(provider__in=provider)
        related_caregivers = []
        for client in related_clients:
            client_caregivers = client.caregiver.all()
            related_caregivers += client_caregivers
        context["current_provider"] = provider[0]
        active_caregivers = CaregiverTimeSheet.objects.filter(client__in=related_clients, caregiver__in=related_caregivers, is_active=True)
        context['active_caregivers'] = active_caregivers
        #Get displayable family contact data
        #Get Tasks for related clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        for client_data in related_clients:
            current_client_tasks = self.get_client_tasks(client_data, request)
            #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
            client_tasks[client_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        context["update_task_form"] = UpdateTaskForm()
        #Get Update Form
        #context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/provider_dashboard_2.html', context)

    @transaction.atomic
    def post(self, request):
        context = {}
        update_task_form = UpdateTaskForm(request.POST, request.FILES)
        #attachments = request.FILES.getlist('attachment')
        are_attachments_valid = True #self.validate_attachments(request, attachments)
        if are_attachments_valid:
            if update_task_form.is_valid():
                current_company = request.user.company
                comment = update_task_form.cleaned_data["comment"]
                task_id = update_task_form.cleaned_data["task_id"]
                client_id = update_task_form.cleaned_data["client_id"]
                client = Client.objects.get(company=current_company,id=client_id)
                #status = update_task_form.cleaned_data["status"]
                #incident_id = update_task_form.cleaned_data["incident_id"]
                #location_id = update_task_form.cleaned_data["location_id"]
                #template_entries = update_task_form.cleaned_data["template_entries"]
                #template_entries = request.POST.getlist('template_entries')
                #print(request.POST)
                #print(template_entries)
                #attachments = request.FILES.getlist('attachment')
                task = TaskSchedule.objects.get(company=current_company,client=client,id=task_id)
                self.save_task_comments(request, update_task_form, task, current_company, client, comment)
                messages.success(request, "Edited Task: {0}".format(task.activity_task))
        return redirect('provider_dashboard')

    def get_client_tasks(self, client_data, request):
        client_timezone = pytz.timezone(client_data.time_zone)
        #current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        timezone.activate(client_timezone)
        client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date).order_by('cancelled','pending','in_progress','complete')
        client_tasks = list(map(lambda x: (x,
        TaskComment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
        TaskAttachment.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
        TaskLink.objects.filter(company=request.user.company,client=client_data,task_schedule=x).order_by('created'),
        self.get_task_template_objects(x, request.user.company)),client_tasks))
        return client_tasks

    def get_task_template_objects(self, client_task, company):
        template_objects = {}
        template_instances = TaskTemplateInstance.objects.filter(company=company,task_schedule=client_task).order_by('created')
        for template_instance in template_instances:
            if template_instance not in template_objects:
                template_objects[template_instance] = {}
            subcategory_instances = TaskTemplateSubcategoryInstance.objects.filter(company=company, task_template_instance=template_instance)
            for subcategory in subcategory_instances:
                entry_instances = list(TaskTemplateEntryInstance.objects.filter(company=company, task_template_subcategory_instance=subcategory))
                template_objects[template_instance][subcategory] = entry_instances
        #print(template_objects)
        return template_objects

    def save_task_comments(self, request, update_task_form, task, current_company, client, comment):

        #caregiver = Caregiver.objects.get(company=current_company,user=request.user)
        task_comment = TaskComment(company=current_company,
                                    client=client,
                                    user=request.user,
                                    task_schedule=task,
                                    comment=comment)
        if comment != "":
            task_comment.save()

class ChooseClientVitals(LoginRequiredMixin, View):

    def get(self, request):
        current_company = request.user.company
        context = {}
        context['client_invoice_form'] = ChooseClientVitalsForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        return render(request, 'production/choose_client_vitals_report.html', context)

class VitalsReport(LoginRequiredMixin, View):

    def get(self, request):
        current_company = request.user.company
        context = {}
        choose_client_vitals_form = ChooseClientVitalsForm(request.GET)
        if choose_client_vitals_form.is_valid():
            client_email = choose_client_vitals_form.cleaned_data['client_email']
            client = Client.objects.get(company=current_company, email_address=client_email)
            start_date = choose_client_vitals_form.cleaned_data['start_date']
            end_date = choose_client_vitals_form.cleaned_data['end_date']

            tasks = TaskSchedule.objects.filter(company=current_company, client=client,
                                    date__range=(start_date, end_date))
            tasks = tasks.order_by('date')
            vitals_templates = []
            vitals_task_templates = []
            for task in tasks:
                vitals_template = self.get_task_template_objects(task, current_company)
                if len(vitals_template)>0:
                    vitals_task_templates.append((task, vitals_template))
                    vitals_templates.append(vitals_template)
            sample_template = TaskTemplateEntry.objects.filter(task_template_code='VIT001').order_by('name')
            context['sample_template'] = sample_template
            context['vitals_task_templates'] = vitals_task_templates
            context['client'] = client
            context['start_date'] = start_date
            context['end_date'] = end_date
        return render(request, 'production/vitals_report.html', context)

    def get_task_template_objects(self, client_task, company):
        template_objects = {}
        template_entry_instances = []
        template_instances = TaskTemplateInstance.objects.filter(company=company,task_schedule=client_task,task_template__template_code='VIT001')
        for template_instance in template_instances:
            if template_instance not in template_objects:
                template_objects[template_instance] = {}
            subcategory_instances = TaskTemplateSubcategoryInstance.objects.filter(company=company, task_template_instance=template_instance)
            for subcategory in subcategory_instances:
                entry_instances = TaskTemplateEntryInstance.objects.filter(company=company,
                    task_template_subcategory_instance=subcategory)
                entry_instances = list(entry_instances.filter(~Q(entry_value='')))
                entry_instances = sorted(entry_instances, key=lambda x: x.task_template_entry.name)
                template_objects[template_instance][subcategory] = entry_instances
                template_entry_instances.extend(entry_instances)
        #print(template_objects)
        return template_entry_instances
