from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def move_manager_dashboard(request):
    return render(request, 'production/move_manager_dashboard.html')

def view_move_projects(request):
    return render(request, 'production/update_move_projects.html')

def view_move_bids(request):
    return render(request, 'production/view_move_bids.html')
