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
