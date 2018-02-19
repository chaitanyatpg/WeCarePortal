from django.shortcuts import render
from django.http import HttpResponse
from django.db import transaction
from mycareportal_app.forms import *
from mycareportal_app.settings_forms import *
from mycareportal_app.models import *
#from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.contrib import messages
from django.db import IntegrityError

from django.contrib.sites.shortcuts import get_current_site

import datetime
import pytz
import django.utils.timezone as timezone

from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from mycareportal_app.common.tokens import account_activation_token
from mycareportal_app.email.care_manager.care_manager_email_processor import CareManagerEmailProcessor
from mycareportal_app.email.caregiver.caregiver_email_processor import CaregiverEmailProcessor
from mycareportal_app.email.user.user_email_processor import UserEmailProcessor
from mycareportal_app.email.admin.admin_email_processor import AdminEmailProcessor

from django.db.models.signals import pre_save
from django.dispatch import receiver

from mycareportal_app.common import error_messaging as error_messaging

from mycareportal_app.common.core.event import Event

class EmailSettings(LoginRequiredMixin, View):

    def get(self, request):
        context = {}

        email_settings_form = EmailSettingsForm(initial=
        {
            'incident_emails': request.user.incident_emails,
            'clock_in_emails': request.user.clock_in_emails,
            'clock_out_emails': request.user.clock_out_emails
        })
        context['email_settings_form'] = email_settings_form
        context['user'] = request.user
        return render(request, "production/email_settings.html", context)

    def post(self, request):
        context = {}
        email_settings_form = EmailSettingsForm(request.POST)
        if email_settings_form.is_valid():
            incident_emails = email_settings_form.cleaned_data['incident_emails']
            clock_in_emails = email_settings_form.cleaned_data['clock_in_emails']
            clock_out_emails = email_settings_form.cleaned_data['clock_out_emails']
            #user = User.objects.get(company=request.user.company, id=request.user.id)
            #user.incident_emails = incident_emails
            #user.clock_in_emails = clock_in_emails
            #user.clock_out_emails = clock_out_emails
            #user.save()
            request.user.incident_emails = incident_emails
            request.user.clock_in_emails = clock_in_emails
            request.user.clock_out_emails = clock_out_emails
            request.user.save()
            #request.user.refresh_from_db()
            messages.success(request, "Saved Email Settings")
        else:
            messages.error(request, "Error saving email settings")
        return redirect('email_settings')
