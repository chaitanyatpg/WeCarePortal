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
            current_client_tasks = self.get_client_tasks(client_data)
            #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
            client_tasks[client_data] = list(current_client_tasks)
        context["client_tasks"] = client_tasks
        #Get Update Form
        #context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/family_dashboard.html', context)

    def get_client_tasks(self, client_data):
        current_date = datetime.date.today()
        client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date)
        return client_tasks
