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

def family_dashboard(request):

    return render(request, 'production/family_dashboard.html')

class FamilyDashboard(View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        family_contact = FamilyContact.objects.get(company=current_company,user=request.user)
        related_clients = Client.objects.filter(company=current_company, family_contacts=family_contact)
        context["current_family_contact"] = family_contact
        #Get displayable family contact data
        name = '{0} {1}'.format(family_contact.first_name, family_contact.last_name)
        address = '{0}, {1} {2} {3}'.format(family_contact.address, family_contact.city, family_contact.state, family_contact.zip_code)
        phone_number = family_contact.phone_number
        relationship = family_contact.relationship
        profile_picture = family_contact.profile_picture.url
        family_contact_data = {'name': name,
                        'address': address,
                        'phone_number': phone_number,
                        'relationship': relationship,
                        'profile_picture': profile_picture}
        context["family_contact_data"] = family_contact_data
        #Get Tasks for related clients for the current day
        client_tasks = {}
        current_date = datetime.date.today()
        for client_data in related_clients:
            current_client_tasks = self.get_client_tasks(client_data)
            print(str(client_data.email_address))
            #client_name = '{0} {1}'.format(client_data.first_name, client_data.last_name)
            client_tasks[client_data] = list(current_client_tasks)
        #print(current_date)
        print(client_tasks[client_data])
        context["client_tasks"] = client_tasks
        #Get Update Form
        #context["update_task_form"] = UpdateTaskForm()
        return render(request, 'production/family_dashboard.html', context)

    def get_client_tasks(self, client_data):
        current_date = datetime.date.today()
        print(current_date)
        client_tasks = TaskSchedule.objects.filter(client=client_data,date=current_date)
        print(len(client_tasks))
        return client_tasks
