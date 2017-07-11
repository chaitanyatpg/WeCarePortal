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
            if care_manager.can_add:
                module_dict['DASHBOARD']['ADDCAREMANAGER']=True
            module_dict['CLIENTPORTAL']['CLIENTONBOARDING']=True
            module_dict['CLIENTPORTAL']['REGISTERTABLETCLIENT']=True
            module_dict['CLIENTPORTAL']['EDITCLIENT']=True
            module_dict['CLIENTPORTAL']['FINDCAREGIVER']=True
            module_dict['CLIENTPORTAL']['ASSIGN_TASKS']=True
            module_dict['CLIENTPORTAL']['CREATE_TASKS']=True
            module_dict['CAREGIVERPORTAL']['CAREGIVERONBOARDING']=True
            module_dict['CAREGIVERPORTAL']['CAREGIVEREDIT']=True
            #module_dict['CAREGIVERPORTAL']['CAREGIVERDASHBOARD']=True
            #module_dict['CAREGIVERPORTAL']['CALENDAR']=True
            #module_dict['FAMILYPORTAL']['FAMILYDASHBOARD']=True
            #module_dict['PROVIDERPORTAL']['PROVIDERDASHBOARD']=True
            module_dict['HOMEASSESSMENTPORTAL']['ASSESSMENTTOOL']=True
            #module_dict['HOMEASSESSMENTPORTAL']['VIEWALERTS']=True
            #module_dict['HOMEMODIFICATIONPORTAL']['CONTRACTORDASHBOARD']=True
            #module_dict['HOMEMODIFICATIONPORTAL']['VIEWALLPROJECTS']=True
            #module_dict['HOMEMODIFICATIONPORTAL']['VIEWBIDS']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['MOVEMANAGERDASHBOARD']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['VIEWMOVEPROJECTS']=True
            #module_dict['MOVEMANAGEMENTPORTAL']['VIEWMOVEBIDS']=True
        #CAREGIVER PERMISSIONS
        if 'CAREGIVER' in user_roles:
            module_dict['CAREGIVERPORTAL']['CAREGIVERDASHBOARD']=True
            #module_dict['CAREGIVERPORTAL']['CALENDAR']=True
        if 'FAMILYUSER' in user_roles:
            module_dict['FAMILYPORTAL']['FAMILYDASHBOARD']=True
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
    return context
