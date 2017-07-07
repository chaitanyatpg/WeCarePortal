from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import View
from mycareportal_app.models import *
from mycareportal_app.assessment_forms import *
from collections import defaultdict

@login_required
def assessment_tool(request):
    return render(request, "production/assessment_tool.html")

@login_required
def view_alerts(request):
    return render(request, "production/view_alerts.html")

class AssessmentChooseClient(LoginRequiredMixin, View):

    def get(self, request):
        context = {}
        current_company = request.user.company
        #context['add_client_form'] = ClientRegistrationForm()
        all_clients = Client.objects.filter(company=current_company).order_by('last_name')
        context['all_clients'] = all_clients
        context['find_client_form'] = FindClientForm()
        return render(request,'production/assessment_choose_client.html', context)

class AssessmentTool(LoginRequiredMixin, View):

    def get(self, request):

        context = {}
        current_company = request.user.company
        find_client_form = FindClientForm(request.GET,request.FILES)
        if find_client_form.is_valid():
            client_email = find_client_form.cleaned_data['client_email']
            client = Client.objects.get(company=current_company, email_address=client_email)
            default_assessment_categories = AssessmentCategories.objects.all()
            assessment_tasks = AssessmentTask.objects.filter(is_default=True) | AssessmentTask.objects.filter(company=current_company)
            client_assessment_map = ClientAssessmentMap.objects.filter(client=client)
            task_map = self.make_task_map(default_assessment_categories, assessment_tasks, client_assessment_map, current_company, client)
            context['task_map'] = task_map
            return render(request, "production/assessment_tool.html", context)

    def make_task_map(self, default_assessment_categories, assessment_tasks, client_assessment_map, company, client):

        task_map = {}
        for category in default_assessment_categories:
            task_map[category] = {}
            for assessment_task in assessment_tasks:
                if assessment_task.assessment_category == category:
                    (assessment_status, created) = client_assessment_map.get_or_create(company=company, client=client, assessment_category=category,assessment_task=assessment_task)
                    task_map[category][assessment_task] = assessment_status
                    assessment_status.save()
        return task_map

@login_required
def post_assessment_status(request):

    if request.method == "POST":
        company = request.user.company;
        status_id = request.POST['status_id']
        status = request.POST['status']
        assessment_map = ClientAssessmentMap.objects.get(company=company,id=status_id)
        assessment_map.status = status
        assessment_map.save()
    return HttpResponse("Changed Status")
