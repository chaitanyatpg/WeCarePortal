from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def contractor_dashboard(request):
    return render(request, 'production/contractor_dashboard.html')

def view_projects(request):
    return render(request, 'production/update_projects.html')

def view_bids(request):
    return render(request, 'production/view_bids.html')
