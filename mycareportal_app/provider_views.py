from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def provider_dashboard(request):
    return render(request, 'production/provider_portal.html')
