from django.db import models
from django.db import transaction
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from PIL import Image
import uuid
import shortuuid
import django.utils.timezone as timezone
import datetime
from datetime import timedelta
import pytz
import vinaigrette
from collections import defaultdict
from mycareportal_app.common.enums import RateType
from mycareportal_app.common.enums import RATE_TYPE_TO_DISPLAY_STRING
# Create your models here.

class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(
            deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)

class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)
    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()

class ActivationCode(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    activation_code = models.CharField(unique=True, max_length = 22, default=shortuuid.uuid, editable=False)
    activated = models.BooleanField(default=False)

def get_company_logo_upload_path(instance, filename):
    return "company_{0}/logo/{1}".format(instance.company_id, filename)

class Company(models.Model):

    admin_dashboard = "ADMIN"
    client_task_dashboard = "CLIENT"
    caregiver_schedule_dashboard = "CAREGIVER"

    DASHBOARD_CHOICES = (
    (admin_dashboard, "ADMIN"),
    (client_task_dashboard, "CLIENT"),
    (caregiver_schedule_dashboard, "CAREGIVER"),
    )

    company_id = models.AutoField(primary_key=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=100,unique=True)
    contact_number = models.CharField(max_length=40)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    time_zone = models.CharField(max_length=50)
    account_number = models.CharField(max_length=250, blank=True, null=True)
    parent_account = models.ForeignKey('self', null=True)
    created = models.DateTimeField(auto_now_add=True)
    activation_code = models.OneToOneField(ActivationCode, null=True)
    activated = models.BooleanField(default=True)
    is_on_free_trial = models.BooleanField(default=False)
    default_dashboard = models.CharField(DASHBOARD_CHOICES, max_length=100, default=admin_dashboard)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    logo = models.ImageField(upload_to=get_company_logo_upload_path, null=True)
    attorney_email = models.EmailField(null=True, blank=True)
    is_parent =models.BooleanField(default=False)
    requires_tablet = models.BooleanField(default=True)
    mileage_rate =   models.DecimalField( max_digits=10, decimal_places=2, null=True)

    def get_child_companies(self):
        children = []
        if self.parent_account_substring != "":
            companies = Company.objects.all()
            for company in companies:
                if (company.account_number != None and len(company.account_number) >=5
                    and company.account_number != self.account_number
                    and company.account_number[:5] == self.parent_account_substring):
                    children.append(company)
        return children

    @property
    def parent_account_substring(self):
        if self.is_parent and len(self.account_number) >= 5:
            return self.account_number[:5]
        else:
            return ""

class User(AbstractUser):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    account_activated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    #email settings
    incident_emails = models.BooleanField(default=True)
    clock_in_emails = models.BooleanField(default=True)
    clock_out_emails = models.BooleanField(default=True)
    task_alert_emails = models.BooleanField(default=True)

class UserRoles(models.Model):

    ROLE_CHOICES = (
    ('CAREMANAGER', 'Care Manager'),
    ('FAMILYUSER', 'Family Member'),
    ('PROVIDERUSER', 'Provider User'),
    ('CAREGIVER', 'Caregiver'),
    ('HOMEMODUSER', 'Home Modification User'),
    ('MOVEMANAGER', 'Move Manager')
    )
    company = models.ForeignKey(Company)
    user = models.ForeignKey(User)
    role = models.CharField(max_length=50,choices=ROLE_CHOICES)
    created = models.DateTimeField(auto_now_add=True)

# This model has been created to store the location i.e lat and long
#  of the user whenever they made login.

class UserLocation(models.Model):
    company = models.ForeignKey(Company)
    user = models.ForeignKey(User)
    user_long = models.CharField(max_length = 200)
    user_lat = models.CharField(max_length = 200)
    created = models.DateTimeField(auto_now_add = True)

class CareManager(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    can_add = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username

class FamilyUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username

class ProviderUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.user.username

def get_caregiver_profile_picture_upload_path(instance, filename):
    return "company_{0}/caregiver/caregiver_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class Caregiver(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email_address = models.CharField(max_length = 100)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=40)
    secondary_phone_number = models.CharField(max_length=40, blank=True)
    ssn = models.CharField(max_length=20, blank=True)
    referrer = models.CharField(max_length=100,blank=True)
    rating = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to=get_caregiver_profile_picture_upload_path)
    hourly_rate = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=1000, blank=True)
    regular_hourly_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_hourly_rate = models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    holiday_hourly_rate = models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_holiday_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    holiday_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_holiday_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)

    #add location
    #add tags

    RATE_TYPE_TO_FIELD = {

        RateType.NORMAL: regular_hourly_rate,
        RateType.WEEKEND: weekend_hourly_rate,
        RateType.HOLIDAY: holiday_hourly_rate,
        RateType.LIVE_IN: live_in_rate,
        RateType.WEEKEND_HOLIDAY: weekend_holiday_rate,
        RateType.WEEKEND_LIVE_IN: weekend_live_in_rate,
        RateType.HOLIDAY_LIVE_IN: holiday_live_in_rate,
        RateType.WEEKEND_HOLIDAY_LIVE_IN: weekend_holiday_live_in_rate
    }


    def __unicode__(self):
        return self.user.username

def get_caregiver_attachment_upload_path(instance, filename):
    return "company_{0}/caregiver/caregiver_{1}/attachments/{2}".format(instance.company.company_id,instance.caregiver.id,filename)

class CaregiverAttachment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    user = models.ForeignKey(User)
    attachment = models.FileField(upload_to=get_caregiver_attachment_upload_path)
    created = models.DateTimeField(auto_now_add=True)

def get_home_mod_user_profile_picture_upload_path(instance, filename):
    return "company_{0}/home_mod/home_mod_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class HomeModificationUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=40)
    profile_picture = models.ImageField(upload_to=get_home_mod_user_profile_picture_upload_path)

    def __unicode__(self):
        return self.user.username

def get_move_manager_profile_picture_upload_path(instance, filename):
    return "company_{0}/move_manager/move_manager_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class MoveManager(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    created = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=40)
    profile_picture = models.ImageField(upload_to=get_move_manager_profile_picture_upload_path)

    def __unicode__(self):
        return self.user.username

def get_family_profile_picture_upload_path(instance, filename):
    return "company_{0}/family/family_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class FamilyContact(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_address = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=40)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    power_of_attorney = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to=get_family_profile_picture_upload_path)
    created = models.DateTimeField(auto_now_add=True)

class Provider(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    email_address = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=40)
    secondary_phone_number = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

class Pharmacy(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=40)
    fax_number = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=400, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

class Payer(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email_address = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    contact_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=40)
    fax_number = models.CharField(max_length=40, blank=True)
    policy_start_date = models.DateField()
    policy_end_date = models.DateField()
    policy_number = models.CharField(max_length=40)
    address = models.CharField(max_length=400, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

def get_client_profile_picture_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class Client(SoftDeletionModel):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    email_address = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=40)
    secondary_phone_number = models.CharField(max_length=40, blank=True)

    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)

    billing_address = models.CharField(max_length=400, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_state = models.CharField(max_length=100, blank=True, null=True)
    billing_zip_code = models.CharField(max_length=10, blank=True, null=True)

    time_zone = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to=get_client_profile_picture_upload_path)

    caregiver = models.ManyToManyField(Caregiver, blank=True)
    family_contacts = models.ManyToManyField(FamilyContact, blank=True)
    provider = models.ManyToManyField(Provider, blank=True)
    pharmacy = models.ManyToManyField(Pharmacy, blank=True)
    payer = models.ManyToManyField(Payer, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    referrer = models.CharField(max_length=100, blank=True)

    notes = models.CharField(max_length=1000, blank=True)
    is_caregiver = models.BooleanField(default=False)
    regular_hourly_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_hourly_rate = models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    holiday_hourly_rate = models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_holiday_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    holiday_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)
    weekend_holiday_live_in_rate =models.DecimalField(max_length = 200,max_digits=10,decimal_places=2,null=True)

    RATE_TYPE_TO_FIELD = {
        RateType.NORMAL: regular_hourly_rate,
        RateType.WEEKEND: weekend_hourly_rate,
        RateType.HOLIDAY: holiday_hourly_rate,
        RateType.LIVE_IN: live_in_rate,
        RateType.WEEKEND_HOLIDAY: weekend_holiday_rate,
        RateType.WEEKEND_LIVE_IN: weekend_live_in_rate,
        RateType.HOLIDAY_LIVE_IN: holiday_live_in_rate,
        RateType.WEEKEND_HOLIDAY_LIVE_IN: weekend_holiday_live_in_rate
    }

def get_client_attachment_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/attachments/{2}".format(instance.company.company_id,instance.client.id,filename)

class ClientAttachment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    attachment = models.FileField(upload_to=get_client_attachment_upload_path)
    created = models.DateTimeField(auto_now_add=True)

class ActivityMaster(models.Model):

    activity_code = models.CharField(max_length=100)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activity_description = models.CharField(max_length=300)

class ActivitySubCategory(models.Model):

    activity_code = models.CharField(max_length=100)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activity_category_code = models.CharField(max_length=100)
    activity_category = models.CharField(max_length=300)

class DefaultTasks(models.Model):

    activity_category_code = models.CharField(max_length=100)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activity_task = models.CharField(max_length=300)
    task_code = models.CharField(max_length=30)

class Tasks(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    activity_task = models.CharField(max_length=300)
    activity_category_code = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

class TaskHeader(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    activity_task = models.CharField(max_length=300)
    start_date = models.DateField()
    end_date = models.DateField()
    task_type = models.CharField(max_length=100)
    start_time = models.CharField(max_length=10, blank=True)
    end_time = models.CharField(max_length=10, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    link = models.CharField(max_length=500, blank=True)
    attachment = models.FileField(upload_to="files/tasks", blank=True)
    created = models.DateTimeField(auto_now_add=True)
    alert_active = models.BooleanField(default=False)

class TaskSchedule(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    task_header = models.ForeignKey(TaskHeader,null=True) #NOTE: change before product to remove null
    activity_task = models.CharField(max_length=300)
    date = models.DateField()
    start_time = models.CharField(max_length=10, blank=True)
    end_time = models.CharField(max_length=10, blank=True)
    pending = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)
    in_progress = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    description = models.CharField(max_length=1000, blank=True)
    link = models.CharField(max_length=500, blank=True)
    attachment = models.FileField(upload_to="files/tasks", blank=True)
    completed_by = models.ForeignKey(User, null=True)
    completed_by_caregiver = models.ForeignKey(Caregiver,null=True)
    completed_timestamp = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    alert_active = models.BooleanField(default=False)
    marked_off = models.BooleanField(default=False)
    marked_off_timestamp = models.DateTimeField(null=True)
    marked_off_user = models.ForeignKey(User, related_name="marked_off_user", null=True)

    def to_json(self):
        json_data = {
            'client': "{0} {1}".format(self.client.first_name, self.client.last_name),
            'date': '{0}-{1}-{2}'.format(self.date.year, self.date.month,
                                        self.date.day),
            'task': self.activity_task,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'status': self.get_current_status()
        }
        return json_data

    def get_current_status(self):
        if self.pending:
            return "PENDING"
        if self.complete:
            return "COMPLETE"
        if self.cancelled:
            return "CANCELLED"
        if self.in_progress:
            return "IN PROGRESS"
        else:
            return "PENDING"

    @staticmethod
    def get_todays_tasks(company, client):
        client_timezone = pytz.timezone(client.time_zone)
        #current_date = datetime.date.today()
        current_date = (timezone.now().astimezone(client_timezone)).date()
        #timezone.activate(client_timezone)
        client_tasks = TaskSchedule.objects.filter(
                                company=company,
                                client=client,
                                date=current_date)
        return client_tasks

    @staticmethod
    def get_all_tasks_for_date(company, client, date):
        client_tasks = TaskSchedule.objects.filter(
                                company=company,
                                client=client,
                                date=date)
        return client_tasks

    def mark_off(self, user):
        self.marked_off = True
        self.marked_off_user = user
        self.marked_off_timestamp = datetime.datetime.now()
        self.save()

class TaskComment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    #caregiver = models.ForeignKey(Caregiver)
    user = models.ForeignKey(User,null=True) #change before final deployment
    task_schedule = models.ForeignKey(TaskSchedule)
    created = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=500)

def get_task_attachment_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/tasks/taskheader_{2}/{3}".format(instance.company.company_id,
                                                        instance.client.id,
                                                        instance.task_schedule.task_header.id,
                                                        filename)

class TaskAttachment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    task_schedule = models.ForeignKey(TaskSchedule)
    attachment = models.FileField(upload_to=get_task_attachment_upload_path)
    created = models.DateTimeField(auto_now_add=True)

class TaskLink(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    task_schedule = models.ForeignKey(TaskSchedule)
    task_url = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

class TaskTemplate(models.Model):

    company = models.ForeignKey(Company, null=True)
    global_template = models.BooleanField(default=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    template_code = models.CharField(max_length=100)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)

class TaskTemplateSubcategory(models.Model):

    company = models.ForeignKey(Company, null=True)
    global_template = models.BooleanField(default=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    template_code = models.CharField(max_length=100)
    template_subcategory_code = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)


class TaskTemplateEntry(models.Model):

    ENTRY_TYPE_CHOICES = (
    ("TEXT", "TEXT"),
    ("CHECK", "CHECK"),
    ("RADIO", "RADIO"),
    ("NUMBER", "NUMBER")
    )

    company = models.ForeignKey(Company, null=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    task_template_code = models.CharField(max_length=100)
    task_template_subcategory_code = models.CharField(max_length=100, null=True)
    task_template_entry_code = models.CharField(max_length=100)
    entry_type = models.CharField(ENTRY_TYPE_CHOICES, max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

vinaigrette.register(TaskTemplateEntry, ['name'])

class TaskTemplateInstance(models.Model):

    company = models.ForeignKey(Company)
    task_template = models.ForeignKey(TaskTemplate)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    task_schedule = models.ForeignKey(TaskSchedule)

class TaskTemplateSubcategoryInstance(models.Model):

    company = models.ForeignKey(Company, null=True)
    task_template_subcategory = models.ForeignKey(TaskTemplateSubcategory)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    task_template_instance = models.ForeignKey(TaskTemplateInstance)

class TaskTemplateEntryInstance(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    task_template_entry = models.ForeignKey(TaskTemplateEntry)
    task_template_subcategory_instance = models.ForeignKey(TaskTemplateSubcategoryInstance, null=True)
    task_template_instance = models.ForeignKey(TaskTemplateInstance)
    entry_value = models.CharField(max_length=500, blank=True)

class AssessmentCategories(models.Model):

    category = models.CharField(max_length=500)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

class AssessmentTask(models.Model):

    assessment_category = models.ForeignKey(AssessmentCategories)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    assessment_task = models.CharField(max_length=2000)
    is_default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True)

class AssessmentTaskCustom(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    assessment_category = models.ForeignKey(AssessmentCategories)
    assessment_task = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

class ClientAssessmentMap(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    assessment_category = models.ForeignKey(AssessmentCategories)
    assessment_task = models.ForeignKey(AssessmentTask)
    status = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)

class ClientTabletRegister(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(Client)
    device_id = models.CharField(max_length=100,unique=True)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverTimeSheet(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    clock_in_timestamp = models.DateTimeField(auto_now_add=True)
    clock_out_timestamp = models.DateTimeField(blank=True, null=True)
    adjusted_clock_out_timestamp = models.DateTimeField(blank=True,null=True)
    adjusted_time_worked = models.DurationField(blank=True,null=True)
    client_timezone = models.CharField(max_length=50)
    time_worked = models.DurationField(blank=True, null=True)
    is_active = models.BooleanField()
    manual_clock_out = models.BooleanField(default=False)
    reason = models.CharField(max_length=200,blank=True)
    created = models.DateTimeField(auto_now_add=True)

class DefaultIncidents(models.Model):

    incident = models.CharField(max_length=150)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    #location = models.CharField(max_length=100, blank=True)
    #reason = models.CharField(max_Length=100, blank=True)
    #trigger_frequency = models.IntegerField()
    #duration = models.CharField(max_length=30, blank=True)
    #duration_frequency = models.IntegerField(blank=True)
    #home_modification = BooleanField()
    #move_management = BooleanField()
    #additional_care = BooleanField()

class IncidentLocations(models.Model):

    location = models.CharField(max_length=100)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

class IncidentReport(models.Model):
    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    reporter = models.ForeignKey(User)
    task = models.ForeignKey(TaskSchedule)
    incident = models.ForeignKey(DefaultIncidents)
    location = models.ForeignKey(IncidentLocations)
    incident_name = models.CharField(max_length=150)
    location_name = models.CharField(max_length=100)
    incident_timestamp = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverScheduleHeader(models.Model):
    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    start_date = models.DateField(null=True) #change b4 prod
    end_date = models.DateField(null=True) #change b4 prod
    start_time = models.TimeField()
    end_time = models.TimeField()
    frequency = models.CharField(max_length=100,blank=True,null=True)
    created = models.DateTimeField(auto_now_add=True)
    live_in = models.BooleanField(default=False)

class CaregiverSchedule(models.Model):
    schedule_header = models.ForeignKey(CaregiverScheduleHeader,null=True) #change b4 production
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_open_schedule_json(company, caregiver, date):
        existing_schedules_for_day = CaregiverSchedule.objects.filter(company=company,
                                                                      caregiver=caregiver,
                                                                      date=date).order_by('start_time')
        #day_start_time_str = '00:00:00'
        #day_start_time = datetime.datetime.strptime(day_start_time_str, '%H:%M:%S')

        #day_end_time_str = '23:59:59'
        #day_end_time = datetime.datetime.strptime(day_end_time_str, '%H:%M:%S')

        day_start_time = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        day_end_time = datetime.datetime.now().replace(hour=23, minute=59, second=59)

        company_timezone = pytz.timezone(company.time_zone)
        

        open_schedule_objects = []

        if not existing_schedules_for_day.exists():
            schedule_object = {
                "id" : "",
                "uid" : "",
                "caregiver_name" : "{0} {1}".format(caregiver.email_address,
                                                    caregiver.last_name),
                
                "client_name" : "",
                'date': '{0}-{1}-{2}'.format(date.year, date.month, date.day),
                'start_time': day_start_time.strftime("%I:%M %p"),
                'end_time': day_end_time.strftime("%I:%M %p"),
                "created" : ""
            }
            open_schedule_objects.append(schedule_object)
            return open_schedule_objects

        current_start = day_start_time.time()
        # current_highest_time = day_end_time
        current_end = day_end_time.time()
        initial_start = day_start_time
        client_timezone = company_timezone
        for schedule in existing_schedules_for_day:
            client_timezone = pytz.timezone(schedule.client.time_zone)
            current_end = datetime.datetime.combine(date, schedule.start_time).astimezone(client_timezone) - timedelta(minutes=1)

            schedule_start_time = current_start.strftime("%I:%M %p")
            schedule_end_time = current_end.strftime("%I:%M %p")
            #schedule_start_time = current_start.time() + 1
            #schedule_end_time = current_end.time() - 1
            schedule_object = {
                "id" : "",
                "uid" : "",
                "caregiver_name" : "{0} {1}".format(caregiver.email_address,
                                                    caregiver.last_name),
                
                "client_name" : "",
                'date': '{0}-{1}-{2}'.format(date.year, date.month, date.day),
                'start_time': schedule_start_time, #current_start.replace(minute=(current_start.minute+1)%60).strftime("%I:%M %p"),
                'end_time': schedule_end_time, #current_end.replace(minute=(current_end.minute-1)%60).strftime("%I:%M %p"),
                "created" : ""
            }
            '''if initial_start is not None:
                temp_datetime = initial_start.astimezone(client_timezone)
                temp_endtime = current_end.astimezone(client_timezone)
                schedule_object['start_time'] = temp_datetime.strftime("%I:%M %p")
                temp_date = temp_datetime - timedelta(days=1)
                schedule_object['date'] = "{0}-{1}-{2}".format(temp_date.year, temp_date.month, temp_date.day)
                initial_start = None'''
            open_schedule_objects.append(schedule_object)
            current_start = (datetime.datetime.combine(date, schedule.end_time).astimezone(client_timezone) + timedelta(minutes=1))# schedule.end_time.replace(minute=(current_end.minute+1)%60)

        current_end = datetime.datetime.combine(date, schedule.start_time) - timedelta(minutes=1)

        schedule_start_time = current_start.strftime("%I:%M %p")
        schedule_end_time = day_end_time.astimezone(company_timezone).strftime("%I:%M %p")
        #schedule_start_time = current_start.time() + 1
        #schedule_end_time = current_end.time() - 1
        schedule_object = {
            "id" : "",
            "uid" : "",
            "caregiver_name" : "{0} {1}".format(caregiver.email_address,
                                                caregiver.last_name),
            
            "client_name" : "",
            'date': '{0}-{1}-{2}'.format(date.year, date.month, date.day),
            'start_time': schedule_start_time, #current_start.replace(minute=(current_start.minute+1)%60).strftime("%I:%M %p"),
            'end_time': schedule_end_time, #current_end.replace(minute=(current_end.minute-1)%60).strftime("%I:%M %p"),
            "created" : ""
        }
        open_schedule_objects.append(schedule_object)

        '''schedule_object = {
            "id" : self.id,
            "uid" : str(self.uid),
            "caregiver_name" : "{0} {1}".format(self.caregiver.first_name,
                                                self.caregiver.last_name),
            "client_name" : "{0} {1}".format(self.client.first_name,
                                            self.client.last_name),
            'date': '{0}-{1}-{2}'.format(schedule_start_datetime.date().year,
                schedule_start_datetime.date().month,
                schedule_start_datetime.date().day),
            'start_time': schedule_start_datetime.time().strftime("%I:%M %p"),
            'end_time': schedule_end_datetime.time().strftime("%I:%M %p"),
            "created" : str(self.created)
        }'''
        
        return open_schedule_objects

    def get_current_client_timestamp(self):
        client = self.client
        client_timezone = pytz.timezone(client.time_zone)
        current_timestamp = (timezone.now().astimezone(client_timezone))
        return current_timestamp

    def is_active(self):
        client = self.client
        client_timezone = pytz.timezone(client.time_zone)
        current_timestamp = (timezone.now().astimezone(client_timezone))
        current_date = current_timestamp.date()
        active_timesheets = CaregiverTimeSheet.objects.filter(company=self.company,
                                                caregiver=self.caregiver,
                                                is_active=True,
                                                clock_out_timestamp=None
                                                )
        caregiver_is_active = False
        for timesheet in active_timesheets:
            if timesheet.clock_in_timestamp.date()==current_date and current_date == self.date:
                caregiver_is_active = True
                break
        return caregiver_is_active

    def is_late(self):
        current_timestamp = self.get_current_client_timestamp()
        current_date = current_timestamp.date()
        if self.date != current_date:
            return False
        if CaregiverTimeSheet.objects.filter(company=self.company,
                    caregiver=self.caregiver,
                    clock_in_timestamp__date=self.date).exists():
            return False
        client = self.client
        client_timezone = pytz.timezone(client.time_zone)
        current_date = current_timestamp.date()
        current_time = current_timestamp.time()
        clock_in_date = self.date
        clock_in_time = self.start_time
        clock_out_time = self.end_time
        if not self.is_active():
            late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
            if clock_in_date == current_date and current_time > late_time:
                return True
        return False

    def is_complete(self):
        current_timestamp = self.get_current_client_timestamp()
        current_date = current_timestamp.date()
        if self.date != current_date:
            return False
        daily_tasks = TaskSchedule.get_todays_tasks(
                                self.company, self.client)
        for task in daily_tasks:
            if not task.complete:
                return False
        return True

    def is_missed(self):
        current_timestamp = self.get_current_client_timestamp()
        current_date = current_timestamp.date()
        if self.date != current_date:
            return False
        # check if date in caregiver schedule is matched by a clock in date
        # in the caregiver timesheet (the clock_in_timestamp)
        matching_timesheets = CaregiverTimeSheet.objects.filter(company=self.company,
                                caregiver=self.caregiver,
                                clock_in_timestamp__date=self.date).exists()
        past_end_time = current_timestamp.time() > self.end_time
        return (not matching_timesheets) and past_end_time

    def get_late_caregivers(company, caregiver_schedule, active_caregivers, caregivers):

        late_caregivers = []
        not_clocked_out_caregivers = []

        for schedule in caregiver_schedule:
            client = schedule.client

            client_timezone = pytz.timezone(client.time_zone)
            #current_date = datetime.date.today()
            current_timestamp = (timezone.now().astimezone(client_timezone))
            current_date = current_timestamp.date()
            current_time = current_timestamp.time()

            clock_in_date = schedule.date
            clock_in_time = schedule.start_time
            clock_out_time = schedule.end_time
            if schedule.caregiver in active_caregivers:
                late_time = clock_out_time.replace(minute=clock_out_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    not_clocked_out_caregivers.append(schedule.caregiver)
            else:
                late_time = clock_in_time.replace(minute=clock_in_time.minute+15)
                if clock_in_date == current_date and current_time > late_time:
                    late_caregivers.append(schedule.caregiver)
        return (late_caregivers, not_clocked_out_caregivers)

    def to_json_schedule(self):
        schedule_start_datetime = datetime.datetime.combine(self.date, self.start_time)
        schedule_end_datetime = datetime.datetime.combine(self.date, self.end_time)
        client_timezone = pytz.timezone(self.client.time_zone)
        #current_date = datetime.date.today()
        schedule_start_datetime = (schedule_start_datetime.astimezone(client_timezone))
        schedule_end_datetime = (schedule_end_datetime.astimezone(client_timezone))
        schedule_object = {
            "id" : self.id,
            "uid" : str(self.uid),
            "caregiver_name" : "{0} {1}".format(self.caregiver.email_address,
                                                self.caregiver.last_name),
            "client_name" : "{0} {1}".format(self.client.first_name,
                                            self.client.last_name),
            'date': '{0}-{1}-{2}'.format(schedule_start_datetime.date().year,
                schedule_start_datetime.date().month,
                schedule_start_datetime.date().day),
            'start_time': schedule_start_datetime.time().strftime("%I:%M %p"),
            'end_time': schedule_end_datetime.time().strftime("%I:%M %p"),
            "created" : str(self.created)
        }
        return schedule_object

    def get_rate_type(self):
        regular = self.is_weekday()
        weekend = self.is_weekend()
        holiday = self.is_holiday()
        live_in = self.is_live_in()
        if weekend and holiday and live_in:
            return RateType.WEEKEND_HOLIDAY_LIVE_IN
        elif weekend and holiday:
            return RateType.WEEKEND_HOLIDAY
        elif holiday and live_in:
            return RateType.HOLIDAY_LIVE_IN
        elif weekend and live_in:
            return RateType.WEEKEND_LIVE_IN
        elif weekend:
            return RateType.WEEKEND
        elif holiday:
            return RateType.HOLIDAY
        elif live_in:
            return RateType.LIVE_IN
        else:
            return RateType.NORMAL

    def is_weekday(self):
        week_num_day = self.date.weekday()
        if week_num_day < 5:
            return True
        else:
            return False

    def is_weekend(self):
        week_num = self.date.weekday()
        if week_num < 5:
            return False
        else:
            return True

    def is_holiday(self):
        if CompanyHolidays.objects.filter(company=self.company,
                                          date = self.date).exists():
            return True
        else:
            return False

    def is_live_in(self):
        if self.schedule_header.live_in:
            return True
        else:
            return False

    def get_hours_diff(self):
        start = datetime.datetime.combine(self.date, self.start_time)
        end = datetime.datetime.combine(self.date, self.end_time)
        diff = end - start
        diff_hours = diff.total_seconds()/3600
        return diff_hours

    def __str__(self):
        return str(self.to_json_schedule())


class ClientMatchCategory(models.Model):
    category = models.CharField(max_length=500)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

class ClientMatchCriteria(models.Model):
    client_match_category = models.ForeignKey(ClientMatchCategory)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    criteria = models.CharField(max_length=2000)
    is_default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True)

class ClientCriteriaMap(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverCriteriaMap(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)

class ClientCertificationMap(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverCertificationMap(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=2)
    created = models.DateTimeField(auto_now_add=True)

class ClientTransferMap(models.Model):

    EXPERIENCE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3)
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    experience = models.IntegerField(EXPERIENCE_CHOICES,null=True)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverTransferMap(models.Model):

    EXPERIENCE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3)
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    experience = models.IntegerField(EXPERIENCE_CHOICES,null=True)
    created = models.DateTimeField(auto_now_add=True)

class HomeModificationTask(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    assessment_category = models.ForeignKey(AssessmentCategories)
    task_name = models.CharField(max_length = 100)
    task_description = models.CharField(max_length = 500)
    created = models.DateTimeField(auto_now_add=True)

    chosen_contractors = models.ManyToManyField(HomeModificationUser, blank=True)
    assigned_contractor = models.ForeignKey(HomeModificationUser, related_name="assigned_contractor", null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    cost = models.IntegerField(null=True)

    #bid = models.ForeignKey(HomeModTaskBid, null=true)
    chosen_bid = models.OneToOneField('HomeModTaskBid', null=True)
    archived = models.BooleanField(default=False)

    @staticmethod
    def get_unarchived_tasks(company):
        tasks = HomeModificationTask.objects.filter(company=company,
                                                    archived=False).order_by('-created')
        return tasks

class HomeModTaskBid(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_task = models.ForeignKey(HomeModificationTask)
    contractor = models.ForeignKey(HomeModificationUser)
    start_date = models.DateField()
    end_date = models.DateField()
    cost = models.IntegerField()
    bid_live = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

class HomeModProject(models.Model):

    ongoing = "Ongoing"
    on_hold = "On Hold"
    cancelled = "Cancelled"
    completed = "Completed"

    STATUS_CHOICES = (
    (ongoing, "Ongoing"),
    (on_hold, "On Hold"),
    (cancelled, "Cancelled"),
    (completed, "Completed")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_task = models.OneToOneField(HomeModificationTask)
    contractor = models.ForeignKey(HomeModificationUser, null=True)
    client = models.ForeignKey(Client, null=True)
    progress = models.IntegerField(default = 0)
    status = models.CharField(STATUS_CHOICES, max_length = 10, default = ongoing)
    estimated_budget = models.IntegerField()
    total_amount_spent = models.IntegerField(default = 0)
    project_duration = models.IntegerField(default = 0)

class HomeModProjectProgressLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_project = models.ForeignKey(HomeModProject)
    progress = models.IntegerField()

class HomeModProjectBudgetLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_project = models.ForeignKey(HomeModProject)
    estimated_budget = models.IntegerField()

class HomeModProjectAmountSpentLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_project = models.ForeignKey(HomeModProject)
    total_amount_spent = models.IntegerField()

class HomeModProjectDurationLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_project = models.ForeignKey(HomeModProject)
    project_duration = models.IntegerField()

class HomeModProjectStatusLog(models.Model):

    ongoing = "Ongoing"
    on_hold = "On Hold"
    cancelled = "Cancelled"
    completed = "Completed"

    STATUS_CHOICES = (
    (ongoing, "Ongoing"),
    (on_hold, "On Hold"),
    (cancelled, "Cancelled"),
    (completed, "Completed")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_project = models.ForeignKey(HomeModProject)
    status = models.CharField(STATUS_CHOICES, max_length = 10)

class MoveManageTask(models.Model):

    type_house = "HOUSE"
    type_townhouse = "TOWNHOUSE"
    type_apartment = "APARTMENT"
    type_senior_facility = "SENIORFACILITY"

    HOME_TYPE_CHOICES = (
    (type_house, "House"),
    (type_townhouse, "Townhouse"),
    (type_apartment, "Apartment"),
    (type_senior_facility, "Senior Facility")
    )

    type_city = "CITY"
    type_urban = "URBAN"
    type_suburban = "SUBURBAN"
    type_rural = "RURAL"

    AREA_TYPE_CHOICES = (
    (type_city, "City"),
    (type_urban, "Urban"),
    (type_suburban, "Suburban"),
    (type_rural, "Rural")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    new_address_max_distance = models.IntegerField()
    type_of_home = models.CharField(HOME_TYPE_CHOICES, max_length=20)
    provides_assistance = models.BooleanField()
    minimum_cost = models.IntegerField()
    maximum_cost = models.IntegerField()
    type_of_area = models.CharField(AREA_TYPE_CHOICES, max_length = 40)
    handicap_friendly = models.BooleanField()
    furnished = models.BooleanField()

    chosen_manager = models.ManyToManyField(MoveManager, blank=True)
    assigned_manager = models.ForeignKey(MoveManager, related_name="assigned_manager", null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    cost = models.IntegerField(null=True)

    #bid = models.ForeignKey(HomeModTaskBid, null=true)
    chosen_bid = models.OneToOneField('MoveManageTaskBid', null=True)
    archived = models.BooleanField(default=False)

    @staticmethod
    def get_unarchived_tasks(company):
        tasks = MoveManageTask.objects.filter(company=company,
                                              archived=False).order_by('-created')
        return tasks

def get_move_inventory_upload_path(instance, filename):
    return "company_{0}/move_inventory/client_{1}/move_task_{2}/inventory/{3}".format(instance.company.company_id,instance.move_manage_task.client.id,instance.move_manage_task.id,filename)

class MoveManageTaskInventory(models.Model):

    type_home = "Home"
    type_store = "Store"
    type_charity = "Charity"
    type_other = "Other"

    DESTINATION_CHOICES = (
    (type_home, "Home"),
    (type_store, "Store"),
    (type_charity, "Charity"),
    (type_other, "Other")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_manage_task = models.ForeignKey(MoveManageTask)
    item = models.CharField(max_length=100)
    item_quantity = models.IntegerField()
    item_price = models.IntegerField(null=True)
    item_sale_price = models.IntegerField(null=True)
    item_destination = models.CharField(DESTINATION_CHOICES, max_length=10, blank=True)
    item_sold = models.BooleanField(default=False)
    item_image = models.ImageField(upload_to=get_move_inventory_upload_path, null=True)

class MoveManageTaskBid(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_manage_task = models.ForeignKey(MoveManageTask)
    move_manager = models.ForeignKey(MoveManager)
    start_date = models.DateField()
    end_date = models.DateField()
    cost = models.IntegerField()
    bid_live = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    

class MoveManagementProject(models.Model):

    ongoing = "Ongoing"
    on_hold = "On Hold"
    cancelled = "Cancelled"
    completed = "Completed"

    STATUS_CHOICES = (
    (ongoing, "Ongoing"),
    (on_hold, "On Hold"),
    (cancelled, "Cancelled"),
    (completed, "Completed")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_manage_task = models.OneToOneField(MoveManageTask)
    move_manager = models.ForeignKey(MoveManager, null=True)
    client = models.ForeignKey(Client, null=True)
    progress = models.IntegerField(default = 0)
    status = models.CharField(STATUS_CHOICES, max_length = 10, default = ongoing)
    estimated_budget = models.IntegerField()
    total_amount_spent = models.IntegerField(default = 0)
    project_duration = models.IntegerField(default = 0)

class MoveProjectProgressLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_management_project = models.ForeignKey(MoveManagementProject)
    progress = models.IntegerField()

class MoveProjectBudgetLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_management_project = models.ForeignKey(MoveManagementProject)
    estimated_budget = models.IntegerField()

class MoveProjectAmountSpentLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_management_project = models.ForeignKey(MoveManagementProject)
    total_amount_spent = models.IntegerField()

class MoveProjectDurationLog(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_management_project = models.ForeignKey(MoveManagementProject)
    project_duration = models.IntegerField()

class MoveProjectStatusLog(models.Model):

    ongoing = "Ongoing"
    on_hold = "On Hold"
    cancelled = "Cancelled"
    completed = "Completed"

    STATUS_CHOICES = (
    (ongoing, "Ongoing"),
    (on_hold, "On Hold"),
    (cancelled, "Cancelled"),
    (completed, "Completed")
    )

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    move_management_project = models.ForeignKey(MoveManagementProject)
    status = models.CharField(STATUS_CHOICES, max_length = 10)

class ClientEndOfLife(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.OneToOneField(Client)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True)
    open = models.BooleanField(default=True)

    @staticmethod
    def get_or_create_eol(company, client):
        if ClientEndOfLife.objects.filter(client=client).exists():
            return ClientEndOfLife.objects.get(company=company, client=client)
        else:
            eol = ClientEndOfLife(company=company, client=client)
            eol.start_date = datetime.datetime.now()
            eol.save()
            return eol

    def get_comments(self):
        comments = EndOfLifeComment.objects.filter(end_of_life=self)
        return comments

    def make_comment(self, comment, company, client, user):
        if comment:
            new_comment = EndOfLifeComment(company=company,
                                            client=client,
                                            user=user,
                                            comment=comment,
                                            end_of_life=self)
            new_comment.save()

    def get_attachments(self):
        attachments = EndOfLifeAttachment.objects.filter(end_of_life=self)
        return attachments

    def close_end_of_life(self):
        self.end_date = datetime.datetime.now()
        self.open = False
        client = self.client
        client_tasks = TaskSchedule.objects.filter(company=client.company,
                                                   client=client)
        for task in client_tasks:
            task.delete()
        client_task_headers = TaskHeader.objects.filter(company=client.company,
                                                        client=client)
        for task_header in client_task_headers:
            task_header.delete()
        self.save()
        self.client.delete()
        self.client.save()

class EndOfLifeComment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    #caregiver = models.ForeignKey(Caregiver)
    user = models.ForeignKey(User,null=True) #change before final deployment
    end_of_life = models.ForeignKey(ClientEndOfLife)
    created = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=500)

def get_end_of_life_attachment_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/end_of_life/end_of_life_{2}/{3}".format(instance.company.company_id,
                                                        instance.client.id,
                                                        instance.end_of_life.id,
                                                        filename)

class EndOfLifeAttachment(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    end_of_life = models.ForeignKey(ClientEndOfLife)
    attachment = models.FileField(upload_to=get_end_of_life_attachment_upload_path)
    created = models.DateTimeField(auto_now_add=True)

class CaregiverScheduleDashboardSettings(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)
    open_filter = models.BooleanField(default=False)
    scheduled_filter = models.BooleanField(default=True)
    in_progress_filter = models.BooleanField(default=False)
    completed_filter = models.BooleanField(default=False)
    late_filter = models.BooleanField(default=False)
    missed_filter = models.BooleanField(default=False)
    caregiver_filter = models.ManyToManyField(Caregiver, blank=True)

    def get_or_create(company, user):
        if CaregiverScheduleDashboardSettings.objects.filter(company=company, user=user).exists():
            return CaregiverScheduleDashboardSettings.objects.get(company=company, user=user)
        else:
            csds = CaregiverScheduleDashboardSettings(company=company,
                                                      user=user)
            csds.save()
            return csds

class UserFcmTokenMap(models.Model):
    user = models.ForeignKey(User)
    fcm_token = models.CharField(max_length=500)
    updated = models.DateTimeField(auto_now_add=True)

    def get_or_create(user, fcm_token):
        if UserFcmTokenMap.objects.filter(user=user).exists():
            return UserFcmTokenMap.objects.get(user=user)
        else:
            new_token = UserFcmTokenMap(user=user, fcm_token=fcm_token)
            new_token.save()

class NotifyClientVitalTask(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company)
    user = models.ForeignKey(User)
    client = models.ForeignKey(Client)

    is_active = models.BooleanField(default=True)
    breathing_issues =models.CharField(max_length=1, blank=True, null=True)
    Cold_or_Cough = models.CharField(max_length=1, blank=True, null=True)
    bad_throat = models.CharField(max_length=1, blank=True, null=True)
    lack_taste_and_smell =models.CharField(max_length=1, blank=True, null=True)
    headache =models.CharField(max_length=1, blank=True, null=True)
    chest_pain=models.CharField(max_length=1, blank=True, null=True)
    weakness = models.CharField(max_length=1, blank=True, null=True)
    fever = models.CharField(max_length=1, blank=True, null=True)
    body_temperature_38_higher =models.CharField(max_length=500, blank=True, null=True)
    blood_oxygen_level_SpO2_95_below = models.CharField(max_length=500, blank=True, null=True)
    heart_rate_bpm_over_100_bpm_under_60_bpm =  models.CharField(max_length=500, blank=True, null=True)
    weight =models.CharField(max_length=100, blank=True, null=True)
    blood_sugar_fasting=models.CharField(max_length=100, blank=True, null=True)
    blood_sugar_non_fasting=models.CharField(max_length=100, blank=True, null=True)
    blood_pressure=models.CharField(max_length=100, blank=True, null=True)

class CompanyHolidays(models.Model):

    company = models.ForeignKey(Company)
    holiday_name = models.CharField(max_length=300, blank=True, null=True)
    description =  models.CharField(max_length = 500,  blank=True, null=True)
    date = models.DateField()

class InvoiceHeader(models.Model):

    INVOICE_NUM_END_LENGTH = 10

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Client)
    total_cost = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.0)
    total_hours = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.0)
    invoice_number_string = models.CharField(max_length=200, unique=True, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    invoice_notes = models.CharField(max_length=1000, blank=True, null=True)
    submitted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default = False)
    taxes =   models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.0)

    @staticmethod
    @transaction.atomic
    def create_invoice(company, client, start_date, end_date):
        invoice_header = InvoiceHeader(company=company,
                                       client=client,
                                       start_date = start_date,
                                       end_date = end_date
                                       )
        invoice_header.save()
        schedules = invoice_header.get_caregiver_schedules()
        caregiver_to_rate_type_to_schedules = invoice_header.group_schedules_by_rate_type(schedules)
        caregiver_to_rate_type_to_total_cost, caregiver_to_rate_type_to_total_hours = invoice_header.get_totals(caregiver_to_rate_type_to_schedules, client)
        (total_hours, total_cost) = invoice_header.create_invoice_lines(caregiver_to_rate_type_to_total_cost,
                                                                        caregiver_to_rate_type_to_total_hours,
                                                                        client)
        invoice_header.total_hours = total_hours
        invoice_header.total_cost = total_cost
       
        invoice_header.invoice_number_string = invoice_header.create_invoice_number_string()
        if invoice_header.total_cost:
            invoice_header.submitted = True
        invoice_header.save()
        return invoice_header

    def get_caregiver_schedules(self):
        schedules = CaregiverSchedule.objects.filter(company=self.company,
                                      client=self.client,
                                      date__range=(self.start_date, self.end_date)
                                      )
        return schedules

    def group_schedules_by_rate_type(self, schedules):
        # Returns caregiver -> rate_type -> schedule list dict
        caregiver_to_rate_type_to_schedules = defaultdict(lambda: defaultdict(list))
        for schedule in schedules:
            rate_type = schedule.get_rate_type()
            
            caregiver_to_rate_type_to_schedules[schedule.caregiver][rate_type].append(schedule)
            
        return caregiver_to_rate_type_to_schedules
     
    def get_totals(self, caregiver_to_rate_type_to_schedules, client):
        # caregiver -> rate_type -> (total_cost, total_hours) tuple
        caregiver_to_rate_type_to_total_cost = defaultdict(lambda: defaultdict(float))
        caregiver_to_rate_type_to_total_hours = defaultdict(lambda: defaultdict(float))
        for caregiver in caregiver_to_rate_type_to_schedules:
            for rate_type in caregiver_to_rate_type_to_schedules[caregiver]:
                for schedule in caregiver_to_rate_type_to_schedules[caregiver][rate_type]:                    
                    if TaskSchedule.objects.filter(client = client.id, date = schedule.date,complete = True).exists():
                        task_schedules = TaskSchedule.objects.filter(client = client.id,  date = schedule.date,complete = True)
                        if task_schedules:
                            if rate_type == RateType.LIVE_IN or rate_type == RateType.WEEKEND_LIVE_IN  or rate_type == RateType.HOLIDAY_LIVE_IN or rate_type == RateType.WEEKEND_HOLIDAY_LIVE_IN:
                                total_hours = 24.0
                                rate = float(getattr(client, client.RATE_TYPE_TO_FIELD[rate_type].attname))
                                if rate < 1.0:
                                    rate_type = RateType.LIVE_IN
                                    rate = float(getattr(client, client.RATE_TYPE_TO_FIELD[RateType.LIVE_IN].attname))
                                    total_cost = rate * total_hours
                                else:
                                    total_cost = rate * total_hours
                                    
                                caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours
                            else:
                                total_hours = schedule.get_hours_diff()
                                rate = float(getattr(client, client.RATE_TYPE_TO_FIELD[rate_type].attname))

                                if rate < 1.0:
                                    rate_type = RateType.NORMAL
                                    rate = float(getattr(client, client.RATE_TYPE_TO_FIELD[RateType.NORMAL].attname))
                                    total_cost = rate * total_hours
                                    caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                    caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours    
                                else:
                                    total_cost = rate * total_hours
                                    caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                    caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours
                      
                                   
                              
                    
                        
        return (caregiver_to_rate_type_to_total_cost, caregiver_to_rate_type_to_total_hours)
    

    def create_invoice_lines(self, caregiver_to_rate_type_to_total_hours,
                             caregiver_to_rate_type_to_total_cost,
                             client):
        # Also returns totals hours, cost
        total_hours = 0.0
        total_cost = 0.0
        for caregiver in caregiver_to_rate_type_to_total_hours:
            for rate_type in caregiver_to_rate_type_to_total_hours[caregiver]:
                cost = caregiver_to_rate_type_to_total_hours[caregiver][rate_type]
                hours = caregiver_to_rate_type_to_total_cost[caregiver][rate_type]
                line_item = InvoiceLineItem(
                    company = self.company,
                    invoice_header = self,
                    caregiver = caregiver,
                    hours = hours,
                    rate_type = RATE_TYPE_TO_DISPLAY_STRING[rate_type],
                    rate = float(getattr(client, client.RATE_TYPE_TO_FIELD[rate_type].attname)),
                    total = cost
                )
                line_item.save()
                total_hours += hours
                total_cost += cost
        return (total_hours, total_cost)

    def create_invoice_number_string(self):
        # Might change later
        # Must run after the invoice header is initially created
        # so that auto added ID's are available

        str_cid = str(self.company.company_id)
        str_month = str(self.created.date().month)
        str_day = str(self.created.date().day)
        str_year = str(self.created.date().year)
        full_invoice_number = ""
        zero_num = self.INVOICE_NUM_END_LENGTH - len(str(self.id))
        for i in range(zero_num):
            full_invoice_number += "0"
        full_invoice_number += str(self.id)
        full_invoice_number_string = "{0}-{1}-{2}-{3}".format(
            str_cid,
            str_month+str_day,
            str_year,
            full_invoice_number
        )
        return full_invoice_number_string

class InvoiceLineItem(models.Model):
    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    invoice_header = models.ForeignKey(InvoiceHeader)
    caregiver = models.ForeignKey(Caregiver)
    hours = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)
    rate_type = models.CharField(max_length=100, choices=RateType.choices())
    rate = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)
    custom_service_charge = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)


class InvoiceRateType(models.Model):
    rate_types = models.CharField(max_length=300)


class CrmClientLead(models.Model):
    company = models.ForeignKey(Company)
    created = models.DateTimeField(auto_now_add=True)
    lead_owner =  models.CharField(max_length=300)
    lead_first_name = models.CharField(max_length=100)
    lead_last_name = models.CharField(max_length=100)
    lead_date_of_birth =models.DateTimeField(null=True)
    gender = models.CharField(max_length=1)
    lead_email_address = models.CharField(max_length = 100,unique=True)
    lead_source = models.CharField(max_length=100)
    lead_contact_number = models.CharField(max_length=40)
    lead_secondary_phone_number = models.CharField(max_length=40, blank=True)
    lead_status =  models.CharField(max_length=100)
    lead_address = models.CharField(max_length=400)
    lead_city = models.CharField(max_length=100)
    lead_state = models.CharField(max_length=100)
    lead_zip_code = models.CharField(max_length=10)
    description = models.CharField(max_length=1000, blank=True)
    

class CrmNotes(models.Model):

    company = models.ForeignKey(Company)
    created = models.DateTimeField(auto_now_add=True)
    crm_client = models.ForeignKey(CrmClientLead)
    notes = models.CharField(max_length=1000, blank=True)




    
class PayrollHeader(models.Model):

    INVOICE_NUM_END_LENGTH = 10

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    caregiver = models.ForeignKey(Caregiver)
    total_cost = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.0)
    total_hours = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.0)
    payroll_number_string = models.CharField(max_length=200, unique=True, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    submitted = models.BooleanField(default=False)
    cancelled = models.BooleanField(default = False)
    


    @staticmethod
    @transaction.atomic
    def create_payroll(company, caregiver, start_date, end_date):
        payroll_header = PayrollHeader(company=company,
                                       caregiver=caregiver,
                                       start_date = start_date,
                                       end_date = end_date
                                       )
        payroll_header.save()
        schedules = payroll_header.get_caregiver_schedules()
        caregiver_to_rate_type_to_schedules = payroll_header.group_schedules_by_rate_type(schedules)
        caregiver_to_rate_type_to_total_cost, caregiver_to_rate_type_to_total_hours = payroll_header.get_totals(caregiver_to_rate_type_to_schedules, caregiver)
        (total_hours, total_cost) = payroll_header.create_payroll_lines(caregiver_to_rate_type_to_total_cost,
                                                                        caregiver_to_rate_type_to_total_hours,
                                                                        caregiver)
        payroll_header.total_hours = total_hours
        payroll_header.total_cost = total_cost
       
        payroll_header.payroll_number_string = payroll_header.create_invoice_number_string()
        if payroll_header.total_cost:
            payroll_header.submitted = True
        payroll_header.save()
        return payroll_header

    def get_caregiver_schedules(self):
        schedules = CaregiverSchedule.objects.filter(company=self.company,
                                      caregiver=self.caregiver,
                                      date__range=(self.start_date, self.end_date)
                                      )
        return schedules
    


    def group_schedules_by_rate_type(self, schedules):
        # Returns caregiver -> rate_type -> schedule list dict
        caregiver_to_rate_type_to_schedules = defaultdict(lambda: defaultdict(list))
        for schedule in schedules:
            rate_type = schedule.get_rate_type()
            
            caregiver_to_rate_type_to_schedules[schedule.caregiver][rate_type].append(schedule)
            
        return caregiver_to_rate_type_to_schedules
    

    def create_invoice_number_string(self):
        # Might change later
        # Must run after the invoice header is initially created
        # so that auto added ID's are available

        str_cid = str(self.company.company_id)
        str_month = str(self.created.date().month)
        str_day = str(self.created.date().day)
        str_year = str(self.created.date().year)
        full_invoice_number = ""
        zero_num = self.INVOICE_NUM_END_LENGTH - len(str(self.id))
        for i in range(zero_num):
            full_invoice_number += "0"
        full_invoice_number += str(self.id)
        full_invoice_number_string = "{0}-{1}-{2}-{3}".format(
            str_cid,
            str_month+str_day,
            str_year,
            full_invoice_number
        )
        return full_invoice_number_string


    def get_totals(self, caregiver_to_rate_type_to_schedules, caregiver):
        # caregiver -> rate_type -> (total_cost, total_hours) tuple
        caregiver_to_rate_type_to_total_cost = defaultdict(lambda: defaultdict(float))
        caregiver_to_rate_type_to_total_hours = defaultdict(lambda: defaultdict(float))
        for caregiver in caregiver_to_rate_type_to_schedules:
            for rate_type in caregiver_to_rate_type_to_schedules[caregiver]:
                for schedule in caregiver_to_rate_type_to_schedules[caregiver][rate_type]:
                    if CaregiverSchedule.objects.filter(caregiver = caregiver.id, date = schedule.date).exists():
                        task_schedules = TaskSchedule.objects.filter(date = schedule.date, start_time = schedule.start_time.strftime("%H:%M"),end_time=schedule.end_time.strftime("%H:%M"),completed_by_caregiver= caregiver.id) 
                        
                        if task_schedules:
                            if rate_type == RateType.LIVE_IN or rate_type == RateType.WEEKEND_LIVE_IN  or rate_type == RateType.HOLIDAY_LIVE_IN or rate_type == RateType.WEEKEND_HOLIDAY_LIVE_IN:
                                total_hours = 24.0
                                rate = float(getattr(caregiver, caregiver.RATE_TYPE_TO_FIELD[rate_type].attname))
                                if rate < 1.0:
                                    rate_type = RateType.LIVE_IN
                                    rate = float(getattr(caregiver, caregiver.RATE_TYPE_TO_FIELD[RateType.LIVE_IN].attname))
                                    total_cost = rate * total_hours
                                else:
                                    total_cost = rate * total_hours
                                    
                                caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours
                            else:
                                total_hours = schedule.get_hours_diff()
                                rate = float(getattr(caregiver, caregiver.RATE_TYPE_TO_FIELD[rate_type].attname))

                                if rate < 1.0:
                                    rate_type = RateType.NORMAL
                                    rate = float(getattr(caregiver, caregiver.RATE_TYPE_TO_FIELD[RateType.NORMAL].attname))
                                    total_cost = rate * total_hours
                                    caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                    caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours    
                                else:
                                    total_cost = rate * total_hours
                                    caregiver_to_rate_type_to_total_cost[caregiver][rate_type] += total_cost
                                    caregiver_to_rate_type_to_total_hours[caregiver][rate_type] += total_hours
                              
        return (caregiver_to_rate_type_to_total_cost, caregiver_to_rate_type_to_total_hours)
    
    def create_payroll_lines(self, caregiver_to_rate_type_to_total_hours,
                             caregiver_to_rate_type_to_total_cost,
                             caregiver):
        # Also returns totals hours, cost
        total_hours = 0.0
        total_cost = 0.0
        for caregiver in caregiver_to_rate_type_to_total_hours:
            for rate_type in caregiver_to_rate_type_to_total_hours[caregiver]:
                cost = caregiver_to_rate_type_to_total_hours[caregiver][rate_type]
                hours = caregiver_to_rate_type_to_total_cost[caregiver][rate_type]
                line_item = PayrollLineItem(
                    company = self.company,
                    payroll_header = self,
                    caregiver = caregiver,
                    hours = hours,
                    rate_type = RATE_TYPE_TO_DISPLAY_STRING[rate_type],
                    rate = float(getattr(caregiver, caregiver.RATE_TYPE_TO_FIELD[rate_type].attname)),
                    total = cost
                )
                line_item.save()
                total_hours += hours
                total_cost += cost
        return (total_hours, total_cost)


class PayrollLineItem(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    payroll_header = models.ForeignKey(PayrollHeader)
    caregiver = models.ForeignKey(Caregiver)
    hours = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)
    rate_type = models.CharField(max_length=100, choices=RateType.choices())
    rate = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)
    custom_service_charge = models.DecimalField(max_length=200, max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_length=200, max_digits=10, decimal_places=2)


class ContractorRejectTask(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    contractor = models.ForeignKey(HomeModificationUser, null=True)
    home_mod_task = models.ForeignKey(HomeModificationTask)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)


class MoveManagerRejectTask(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    move_manager = models.ForeignKey(MoveManager, null=True)
    move_manage_task = models.ForeignKey(MoveManageTask)
    status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)



class StateField(models.Model):
    state_name = models.CharField(max_length=300)



