from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from PIL import Image
# Create your models here.

class Company(models.Model):

    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=100,unique=True)
    contact_number = models.CharField(max_length=40)
    address = models.CharField(max_length=400)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    time_zone = models.CharField(max_length=50, blank=True)
    account_number = models.IntegerField(unique=True, null=True)
    parent_account = models.ForeignKey('self', null=True)

class User(AbstractUser):

    company = models.ForeignKey(Company)

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

class CareManager(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)
    can_add = models.BooleanField(default=True)

    def __unicode__(self):
        return self.user.username

class FamilyUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.user.username

class ProviderUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.user.username

def get_caregiver_profile_picture_upload_path(instance, filename):
    return "company_{0}/caregiver/caregiver_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class Caregiver(models.Model):

    company = models.ForeignKey(Company)
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
    ssn = models.CharField(max_length=20)
    referrer = models.CharField(max_length=100,blank=True)
    rating = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to=get_caregiver_profile_picture_upload_path)
    #add location
    #add tags

    def __unicode__(self):
        return self.user.username

class HomeModificationUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.user.username

class MoveManager(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company)
    email_address = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.user.username

def get_family_profile_picture_upload_path(instance, filename):
    return "company_{0}/family/family_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class FamilyContact(models.Model):

    company = models.ForeignKey(Company)
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

class Provider(models.Model):

    company = models.ForeignKey(Company)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_address = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    provider_type = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=40)
    secondary_phone_number = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

class Pharmacy(models.Model):

    company = models.ForeignKey(Company)
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

class Payer(models.Model):

    company = models.ForeignKey(Company)
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

def get_client_profile_picture_upload_path(instance, filename):
    return "company_{0}/client/client_{1}/profile_pictures/{2}".format(instance.company.company_id,instance.id,filename)

class Client(models.Model):

    company = models.ForeignKey(Company)
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

class ActivityMaster(models.Model):

    activity_code = models.CharField(max_length=100)
    activity_description = models.CharField(max_length=300)

class ActivitySubCategory(models.Model):

    activity_code = models.CharField(max_length=100)
    activity_category_code = models.CharField(max_length=100)
    activity_category = models.CharField(max_length=300)

class DefaultTasks(models.Model):

    activity_category_code = models.CharField(max_length=100)
    activity_task = models.CharField(max_length=300)
    task_code = models.CharField(max_length=30)

class Tasks(models.Model):

    company = models.ForeignKey(Company)
    activity_task = models.CharField(max_length=300)
    activity_category_code = models.CharField(max_length=100)

class TaskHeader(models.Model):

    company = models.ForeignKey(Company)
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

class TaskSchedule(models.Model):

    company = models.ForeignKey(Company)
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

class TaskComment(models.Model):

    company = models.ForeignKey(Company)
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
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    task_schedule = models.ForeignKey(TaskSchedule)
    attachment = models.FileField(upload_to=get_task_attachment_upload_path)
    created = models.DateTimeField(auto_now_add=True)

class TaskLink(models.Model):

    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    user = models.ForeignKey(User)
    task_schedule = models.ForeignKey(TaskSchedule)
    task_url = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

class AssessmentCategories(models.Model):

    category = models.CharField(max_length=500)

class AssessmentTask(models.Model):

    assessment_category = models.ForeignKey(AssessmentCategories)
    assessment_task = models.CharField(max_length=2000)
    is_default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True)

class AssessmentTaskCustom(models.Model):

    company = models.ForeignKey(Company)
    assessment_category = models.ForeignKey(AssessmentCategories)
    assessment_task = models.CharField(max_length=2000)

class ClientAssessmentMap(models.Model):

    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    assessment_category = models.ForeignKey(AssessmentCategories)
    assessment_task = models.ForeignKey(AssessmentTask)
    status = models.CharField(max_length=2)

class ClientTabletRegister(models.Model):

    company = models.ForeignKey(Company)
    client = models.OneToOneField(Client)
    device_id = models.CharField(max_length=100,unique=True)

class CaregiverTimeSheet(models.Model):

    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    clock_in_timestamp = models.DateTimeField(auto_now_add=True)
    clock_out_timestamp = models.DateTimeField(blank=True, null=True)
    client_timezone = models.CharField(max_length=50)
    time_worked = models.DurationField(blank=True, null=True)
    is_active = models.BooleanField()

class DefaultIncidents(models.Model):

    incident = models.CharField(max_length=150)
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

class IncidentReport(models.Model):
    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    reporter = models.ForeignKey(User)
    task = models.ForeignKey(TaskSchedule)
    incident = models.ForeignKey(DefaultIncidents)
    location = models.ForeignKey(IncidentLocations)
    incident_name = models.CharField(max_length=150)
    location_name = models.CharField(max_length=100)
    incident_timestamp = models.DateTimeField(auto_now_add=True)

class CaregiverScheduleHeader(models.Model):
    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    start_date = models.DateField(null=True) #change b4 prod
    end_date = models.DateField(null=True) #change b4 prod
    start_time = models.TimeField()
    end_time = models.TimeField()

class CaregiverSchedule(models.Model):
    schedule_header = models.ForeignKey(CaregiverScheduleHeader,null=True) #change b4 production
    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client = models.ForeignKey(Client)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

class ClientMatchCategory(models.Model):
    category = models.CharField(max_length=500)

class ClientMatchCriteria(models.Model):
    client_match_category = models.ForeignKey(ClientMatchCategory)
    criteria = models.CharField(max_length=2000)
    is_default = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True)

class ClientCriteriaMap(models.Model):

    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)

class CaregiverCriteriaMap(models.Model):

    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)

class ClientCertificationMap(models.Model):

    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    status = models.CharField(max_length=2)

class CaregiverCertificationMap(models.Model):

    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    status = models.CharField(max_length=2)

class ClientTransferMap(models.Model):

    EXPERIENCE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3)
    )

    company = models.ForeignKey(Company)
    client = models.ForeignKey(Client)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    experience = models.IntegerField(EXPERIENCE_CHOICES,null=True)

class CaregiverTransferMap(models.Model):

    EXPERIENCE_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3)
    )

    company = models.ForeignKey(Company)
    caregiver = models.ForeignKey(Caregiver)
    client_match_category = models.ForeignKey(ClientMatchCategory)
    client_match_criteria = models.ForeignKey(ClientMatchCriteria)
    experience = models.IntegerField(EXPERIENCE_CHOICES,null=True)
