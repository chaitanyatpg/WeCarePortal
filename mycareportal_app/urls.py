from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import client_views
from . import caregiver_views
from . import family_views
from . import provider_views
from . import assessment_views
from . import home_mod_views
from . import move_manage_views
from . import reporting_views
from django.contrib.auth import views as auth_views

"""urlpatterns = [
    url(r'^$', auth_views.login, {'template_name': 'login.html'},name='Login'),
    url(r'^register-user$', social_net_views.register_user, name='Register'),
    url(r'^login$', auth_views.login, {'template_name': 'login.html'},name='Login'),
    url(r'^global-stream$', social_net_views.global_stream, name='GlobalStream'),
    url(r'^profile$', social_net_views.profile, name='Profile'),
]
"""
urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view(template_name='production/wecare_login.html'),name='login'),
    url(r'^home$', views.home,name='home'),
    url(r'^login$', auth_views.LoginView.as_view(template_name='production/wecare_login.html'),name='login'),
    url(r'^logout$', views.logout_view,name='logout'),
    url(r'^register',views.register,name='register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^pwd_activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.pwd_activate, name='pwd_activate'),
    url(r'^forgot_password', views.ForgotPassword.as_view(),name='forgot_password'),
    url(r'^reset_password',views.reset_password,name='reset_password'),
    url(r'^edit_company', views.EditCompany.as_view(), name='edit_company'),
    url(r'^dashboard',views.dashboard,name='dashboard'),
    url(r'^action_log',views.ViewActionLog.as_view(),name='action_log'),
    url(r'^date_filter_dashboard',views.date_filter_dashboard,name='date_filter_dashboard'),
    url(r'^view_active_caregivers',views.ViewActiveCaregivers.as_view(),name='view_active_caregivers'),
    url(r'^view_daily_incidents', views.ViewDailyIncidents.as_view(),name='view_daily_incidents'),
    url(r'^choose_view_client_incidents', client_views.ChooseViewClientIncidents.as_view(),name='choose_view_client_incidents'),
    url(r'^view_incidents_by_client', client_views.ViewIncidentsByClient.as_view(),name='view_incidents_by_client'),
    url(r'^set_tablet_id_session',views.set_tablet_id_session,name='set_tablet_id_session'),
    url(r'^set_caregiver_time_sheet_session', views.set_caregiver_time_sheet_session,name='set_caregiver_time_sheet_session'),
    url(r'^end_caregiver_time_sheet_session', views.end_caregiver_time_sheet_session,name='end_caregiver_time_sheet_session'),
    url(r'^add_care_manager',views.AddCareManager.as_view(),name='add_care_manager'),
    url(r'^activate_tablet_choose_client',client_views.ActivateTabletChooseClient.as_view(),name='activate_tablet_choose_client'),
    url(r'^activate_tablet_client',client_views.ActivateTabletClient.as_view(),name='activate_tablet_client'),
    url(r'^add_client',client_views.AddClient.as_view(),name='add_client'),
    url(r'^edit_choose_client',client_views.EditChooseClient.as_view(),name='edit_choose_client'),
    url(r'^post_family_details',client_views.post_family_details,name='post_family_details'),
    url(r'^post_provider_details',client_views.post_provider_details,name='post_provider_details'),
    url(r'^post_pharmacy_details',client_views.post_pharmacy_details,name='post_pharmacy_details'),
    url(r'^post_payer_details',client_views.post_payer_details,name='post_payer_details'),
    url(r'^edit_client',client_views.EditClient.as_view(),name='edit_client'),
    url(r'^post_criteria',client_views.post_criteria,name='post_criteria'),
    url(r'^post_certification',client_views.post_certification,name='post_certification'),
    url(r'^post_transfer',client_views.post_transfer,name='post_transfer'),
    url(r'^caregiver_post_criteria',caregiver_views.caregiver_post_criteria,name='caregiver_post_criteria'),
    url(r'^caregiver_post_certification',caregiver_views.caregiver_post_certification,name='caregiver_post_certification'),
    url(r'^caregiver_post_transfer',caregiver_views.caregiver_post_transfer,name='caregiver_post_transfer'),
    #url(r'^edit_client/client_email=(?P<client_email>.*)$',client_views.EditClient.as_view(),name='edit_client'),
    url(r'^get_family_with_id',client_views.get_family_with_id,name='get_family_with_id'),
    url(r'^get_provider_with_id',client_views.get_provider_with_id,name='get_provider_with_id'),
    url(r'^get_pharmacy_with_id',client_views.get_pharmacy_with_id,name='get_pharmacy_with_id'),
    url(r'^get_payer_with_id',client_views.get_payer_with_id,name='get_payer_with_id'),
    url(r'^delete_family_member',client_views.delete_family_member,name='delete_family_member'),
    url(r'^delete_provider',client_views.delete_provider,name='delete_provider'),
    url(r'^delete_pharmacy',client_views.delete_pharmacy,name='delete_pharmacy'),
    url(r'^delete_payer',client_views.delete_payer,name='delete_payer'),
    url(r'^find_caregiver',client_views.FindCaregiver.as_view(),name='find_caregiver'),
    url(r'^choose_caregiver/(?P<client_email>\w+)/$', client_views.ChooseCaregiver.as_view(),name='choose_caregiver'),
    url(r'^choose_caregiver', client_views.ChooseCaregiver.as_view(),name='choose_caregiver'),
    url(r'^select_shifts_choose', caregiver_views.SelectShiftsChoose.as_view(),name='select_shifts_choose'),
    url(r'^schedule_shifts', caregiver_views.ScheduleShifts.as_view(),name='schedule_shifts'),
    url(r'^get_schedule_with_id', caregiver_views.get_schedule_with_id,name='get_schedule_with_id'),
    url(r'^edit_schedule_with_id', caregiver_views.edit_schedule_with_id,name='edit_schedule_with_id'),
    url(r'^delete_schedule_with_id', caregiver_views.delete_schedule_with_id,name='delete_schedule_with_id'),
    url(r'^delete_recurring_schedule_with_id', caregiver_views.delete_recurring_schedule_with_id,name='delete_recurring_schedule_with_id'),
    url(r'^get_assigned_clients_with_caregiver_with_id', caregiver_views.get_assigned_clients_with_caregiver_with_id,name='get_assigned_clients_with_caregiver_with_id'),
    url(r'^get_client_with_email', client_views.get_client_with_email,name='get_client_with_email'),
    url(r'^get_sub_categories', client_views.get_sub_categories,name='get_sub_categories'),
    url(r'^assign_choose_client', client_views.AssignTasksChooseClient.as_view(),name='assign_choose_client'),
    url(r'^assign_tasks',client_views.AssignTasks.as_view(),name='assign_tasks'),
    url(r'^create_tasks', client_views.CreateTasks.as_view(),name='create_tasks'),
    url(r'^get_task_with_id', client_views.get_task_with_id,name='get_task_with_id'),
    url(r'^edit_task_with_id', client_views.edit_task_with_id,name='edit_task_with_id'),
    url(r'^delete_task_with_id', client_views.delete_task_with_id,name='delete_task_with_id'),
    url(r'^delete_recurring_task_with_id', client_views.delete_recurring_task_with_id,name='delete_recurring_task_with_id'),
    url(r'^add_caregiver',caregiver_views.AddCaregiver.as_view(),name='add_caregiver'),
    url(r'^edit_choose_caregiver', caregiver_views.EditChooseCaregiver.as_view(),name='edit_choose_caregiver'),
    url(r'^choose_view_caregiver_timesheet', caregiver_views.ChooseViewCaregiverTimesheet.as_view(),name='choose_view_caregiver_timesheet'),
    url(r'^view_caregiver_timesheet', caregiver_views.ViewCaregiverTimesheet.as_view(),name='view_caregiver_timesheet'),
    url(r'^export_all_caregiver_timesheets/csv/$', caregiver_views.export_all_caregiver_timesheets, name='export_all_caregiver_timesheets'),
    url(r'^get_caregiver_with_email', caregiver_views.get_caregiver_with_email,name='get_caregiver_with_email'),
    url(r'^edit_caregiver', caregiver_views.EditCaregiver.as_view(),name='edit_caregiver'),
    url(r'^caregiver_dashboard',caregiver_views.CaregiverDashboard.as_view(),name=
    'caregiver_dashboard'),
    url(r'^calendar',caregiver_views.calendar,name='calendar'),
    url(r'^family_dashboard',family_views.FamilyDashboard.as_view(),name=
    'family_dashboard'),
    url(r'^provider_dashboard',provider_views.ProviderDashboard.as_view(),name=
    'provider_dashboard'),
    url(r'^assessment_choose_client',assessment_views.AssessmentChooseClient.as_view(),name='assessment_choose_client'),
    url(r'^assessment_tool',assessment_views.AssessmentTool.as_view(),name=
    'assessment_tool'),
    url(r'^post_assessment_status',assessment_views.post_assessment_status,name='post_assessment_status'),
    url(r'^view_alerts',assessment_views.view_alerts,name='view_alerts'),
    url(r'^contractor_dashboard',home_mod_views.contractor_dashboard,name=
    'contractor_dashboard'),
    url(r'^view_projects',home_mod_views.view_projects,name='view_projects'),
    url(r'^view_bids',home_mod_views.view_bids,name='view_bids'),
    url(r'^move_manager_dashboard',move_manage_views.move_manager_dashboard,
    name='move_manager_dashboard'),
    url(r'^view_move_projects',move_manage_views.view_move_projects,
    name='view_move_projects'),
    url(r'^view_move_bids',move_manage_views.view_move_bids,
    name='view_move_bids'),
    url(r'^view_all_caregivers', reporting_views.ViewAllCaregivers.as_view(),name='view_all_caregivers'),
    url(r'^view_all_clients', reporting_views.ViewAllClients.as_view(),name='view_all_clients'),
    url(r'^view_clients_without_caregivers', reporting_views.ViewClientsWithoutCaregiver.as_view(),name='view_clients_without_caregivers')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
