from mycareportal_app.models import *
from collections import defaultdict

def add_roles_to_context(request):
    context = {}
    if request.user.id != None:
        user_roles = UserRoles.objects.filter(user=request.user)
        user_roles = [x.role for x in user_roles]
        module_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(bool)))
        modules = ['DASHBOARD',
                    'CLIENTPORTAL',
                    'CAREGIVERPORTAL',
                    'FAMILYPORTAL'
                    'PROVIDERPORTAL',
                    'HOMEASSESSMENTPORTAL',
                    'HOMEMODIFICATIONPORTAL',
                    'MOVEMANAGEMENTPORTAL']
        module_tabs = [['ADMINDASHBOARD','ADDCAREMANAGER'],
                    ['CLIENTONBOARDING','FINDCAREGIVER','ASSIGN_TASKS','CREATE_TASKS','REGISTERTABLETCLIENT'],
                    ['CAREGIVERONBOARDING','EDIT_CAREGIVER','CAREGIVERDASHBOARD','CALENDAR'],
                    ['FAMILYDASHBOARD'],
                    ['PROVIDERDASHBOARD'],
                    ['ASSESSMENTTOOL','VIEWALERTS'],
                    ['CONTRACTORDASHBOARD','VIEWALLPROJECTS','VIEWBIDS'],
                    ['MOVEMANAGERDASHBOARD','VIEWMOVEPROJECTS','VIEWMOVEBIDS']]
        roles = ['CAREMANAGER',
                'FAMILYUSER',
                'PROVIDERUSER',
                'CAREGIVER',
                'HOMEMODUSER',
                'MOVEMANAGER']
        #CAREMANAGER PERMISSIONS
        if 'CAREMANAGER' in user_roles:
            care_manager = CareManager.objects.get(user=request.user)
            module_dict['DASHBOARD']['ADMINDASHBOARD']=True
            module_dict['DASHBOARD']['CAREGIVER_SCHEDULE_DASHBOARD']=True
            module_dict['DASHBOARD']['CLIENT_TASK_DASHBOARD']=True
            module_dict['DASHBOARD']['ACTIONLOG']=True
            if care_manager.can_add:
                module_dict['DASHBOARD']['ADDCAREMANAGER']=True
                module_dict['REPORTING']['VIEWALLCAREMANAGERS']=True
            module_dict['DASHBOARD']['EDITCOMPANY']=True
            module_dict['DASHBOARD']['VIEWACTIVECAREGIVERS']=True
            module_dict['DASHBOARD']['VIEWCAREGIVERTIMESHEET']=True
            module_dict['DASHBOARD']['VIEWDAILYINCIDENTS']=True
            module_dict['DASHBOARD']['VIEWLOCATIONLOGS']=True
		    
            module_dict['DASHBOARD']['VIEWCLIENTHIGHRISK']=True
            module_dict['CLIENTPORTAL']['VIEWINCIDENTSBYCLIENT']=True
            module_dict['CLIENTPORTAL']['CLIENTONBOARDING']=True
            module_dict['CLIENTPORTAL']['REGISTERTABLETCLIENT']=True
            module_dict['CLIENTPORTAL']['EDITCLIENT']=True
            module_dict['CLIENTPORTAL']['FINDCAREGIVER']=True
            module_dict['CLIENTPORTAL']['ASSIGN_TASKS']=True
            module_dict['CLIENTPORTAL']['CREATE_TASKS']=True
            module_dict['CLIENTPORTAL']['LEGAL_EMAIL']=True
            module_dict['CLIENTPORTAL']['MANAGER_CLIENT_DASHBOARD']=True
            module_dict['CLIENTPORTAL']['CHOOSE_CLIENT_INVOICE']=True
            module_dict['CLIENTPORTAL']['DEACTIVATE_CLIENT']=True
            module_dict['CLIENTPORTAL']['CLIENT_END_OF_LIFE']=True
            module_dict['CAREGIVERPORTAL']['CAREGIVERONBOARDING']=True
            module_dict['CAREGIVERPORTAL']['CAREGIVEREDIT']=True
            module_dict['CAREGIVERPORTAL']['SCHEDULESHIFTS']=True
            module_dict['CAREGIVERPORTAL']['SCHEDULEFREECAREGIVER']=True
            #module_dict['CAREGIVERPORTAL']['CAREGIVERDASHBOARD']=True
            #module_dict['CAREGIVERPORTAL']['CALENDAR']=True
            #module_dict['FAMILYPORTAL']['FAMILYDASHBOARD']=True
            #module_dict['PROVIDERPORTAL']['PROVIDERDASHBOARD']=True
            module_dict['HOMEASSESSMENTPORTAL']['ASSESSMENTTOOL']=True
            module_dict['HOMEASSESSMENTPORTAL']['HOMEDASHBOARD']=True
            #module_dict['HOMEASSESSMENTPORTAL']['VIEWALERTS']=True
            module_dict['HOMEMODIFICATIONPORTAL']['ADDHOMEMODMANAGER'] = True
            module_dict['HOMEMODIFICATIONPORTAL']['EDITHOMEMODMANAGER'] = True
            #module_dict['HOMEMODIFICATIONPORTAL']['CONTRACTORDASHBOARD']=True
            #module_dict['HOMEMODIFICATIONPORTAL']['VIEWALLPROJECTS']=True
            #module_dict['HOMEMODIFICATIONPORTAL']['VIEWBIDS']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['MOVEMANAGERDASHBOARD']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['VIEWMOVEPROJECTS']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['VIEWMOVEBIDS']=True
            module_dict['MOVEMANAGEMENTPORTAL']['ADDMOVEMANAGER'] = True
            module_dict['MOVEMANAGEMENTPORTAL']['EDITMOVEMANAGER'] = True

            module_dict['REPORTING']['VIEWALLCLIENTS']=True
            module_dict['REPORTING']['VIEWALLCAREGIVERS']=True
            module_dict['REPORTING']['VIEWALLCLIENTSWITHOUTCAREGIVERS']=True
            module_dict['REPORTING']['VIEWDAILYACTIVITYREPORT']=True
            module_dict['PROVIDERPORTAL']['VITALSREPORT']=True

        #CAREGIVER PERMISSIONS
        if 'CAREGIVER' in user_roles:
            module_dict['CAREGIVERPORTAL']['CAREGIVERDASHBOARD']=True
            module_dict['CAREGIVERPORTAL']['VIEWCALENDAR']=True
            module_dict['CAREGIVERPORTAL']['VIEWSHIFTS']=True
            #module_dict['CAREGIVERPORTAL']['CALENDAR']=True
        if 'FAMILYUSER' in user_roles:
            module_dict['FAMILYPORTAL']['FAMILYDASHBOARD']=True
            module_dict['FAMILYPORTAL']['LEGAL_EMAIL']=True
        if 'HOMEMODUSER' in user_roles:
            module_dict['HOMEMODIFICATIONPORTAL']['CONTRACTORDASHBOARD']=True
            module_dict['HOMEMODIFICATIONPORTAL']['VIEWALLPROJECTS']=True
        if 'MOVEMANAGER' in user_roles:
            module_dict['MOVEMANAGEMENTPORTAL']['UPDATEMOVEPROJECTS'] = True
            module_dict['MOVEMANAGEMENTPORTAL']['MOVEMANAGERDASHBOARD'] = True
            module_dict['MOVEMANAGEMENTPORTAL']['VIEWMOVEPROJECTS'] = True
        if 'PROVIDERUSER' in user_roles:
            module_dict['PROVIDERPORTAL']['DASHBOARD']=True
            module_dict['PROVIDERPORTAL']['VITALSREPORT']=True
        module_dict['SETTINGS']['EMAILSETTINGS']=True
        context['user_roles'] = user_roles
        context['module_dict']= module_dict
    return context

def add_current_user_context(request):
    context = {}
    if request.user.id != None:
        user_roles = UserRoles.objects.filter(user=request.user)
        user_roles = [x.role for x in user_roles]
        if 'CAREGIVER' in user_roles:
            auth_info = Caregiver.objects.get(user=request.user)
            context['current_user_info'] = auth_info
        if 'FAMILYUSER' in user_roles:
            auth_info = FamilyContact.objects.get(user=request.user)
            context['current_user_info'] = auth_info
        if 'CAREMANAGER' in user_roles:
            auth_info = CareManager.objects.get(user=request.user)
            context['current_user_info'] = auth_info
    return context

def add_tablet_id_context(request):
    context = {}
    if "tablet_id" in request.session:
        context["global_tablet_id"] = request.session["tablet_id"]
    return context
