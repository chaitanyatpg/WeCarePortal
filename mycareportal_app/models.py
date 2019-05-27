from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from PIL import Image
import uuid
import shortuuid
# Create your models here.

class ActivationCode(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    activation_code = models.CharField(unique=True, max_length = 22, default=shortuuid.uuid, editable=False)
    activated = models.BooleanField(default=False)

class Company(models.Model):

    company_id = models.AutoField(primary_key=True)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=100,unique=True)
    contact_number = models.CharField(max_length=40)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    time_zone = models.CharField(max_length=50)
    account_number = models.IntegerField(unique=True, null=True)
    parent_account = models.ForeignKey('self', null=True)
    created = models.DateTimeField(auto_now_add=True)
    activation_code = models.OneToOneField(ActivationCode, null=True)
    activated = models.BooleanField(default=True)
    is_on_free_trial = models.BooleanField(default=False)

class User(AbstractUser):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    account_activated = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    #email settings
    incident_emails = models.BooleanField(default=True)
    clock_in_emails = models.BooleanField(default=True)
    clock_out_emails = models.BooleanField(default=True)

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
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateTimeField()
    phone_number = models.CharField(max_length=40)
    secondary_phone_number = models.CharField(max_length=40, blank=True)
    ssn = models.CharField(max_length=20, blank=True)
    referrer = models.CharField(max_length=100,blank=True)
    rating = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to=get_caregiver_profile_picture_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    #add location
    #add tags

    def __unicode__(self):
        return self.user.username

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
    state = models.CharField(max_length=2)
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
    state = models.CharField(max_length=2)
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
    state = models.CharField(max_length=2)
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
    state = models.CharField(max_length=2, blank=True)
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
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

def get_client_profile_picture_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class Client(models.Model):

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
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
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
    created = models.DateTimeField(auto_now_add=True)

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
    task_template_entry_code = models.CharField(max_length=100)
    entry_type = models.CharField(ENTRY_TYPE_CHOICES, max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

class TaskTemplateInstance(models.Model):

    company = models.ForeignKey(Company)
    task_template = models.ForeignKey(TaskTemplate)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    task_schedule = models.ForeignKey(TaskSchedule)

class TaskTemplateEntryInstance(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    task_template_entry = models.ForeignKey(TaskTemplateEntry)
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
    created = models.DateTimeField(auto_now_add=True)

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

class HomeModTaskBid(models.Model):

    company = models.ForeignKey(Company)
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    home_mod_task = models.ForeignKey(HomeModificationTask)
    contractor = models.ForeignKey(HomeModificationUser)
    start_date = models.DateField()
    end_date = models.DateField()
    cost = models.IntegerField()

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
    state = models.CharField(max_length=2)
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
