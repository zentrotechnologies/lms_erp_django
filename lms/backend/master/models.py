from django.db import models
from django.utils.translation import gettext_lazy as _
from helpers.models import TrackingModel




# course category
class Category(TrackingModel):
    category_name = models.CharField(max_length=255, null=True, blank=True)
    tags = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
class Sub_Category(TrackingModel):
    category_id = models.IntegerField(null=True, blank=True, db_index=True)
    sub_name = models.CharField(max_length=255)
    tags = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)
class College(TrackingModel):
    college_code = models.CharField(max_length=50, unique=True)
    college_name = models.CharField(max_length=255)
    university_name = models.CharField(max_length=255, null=True, blank=True)
    affiliation_number = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)

    
class AcademicYear(TrackingModel):
    academic_year_name = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    admission_start_date = models.DateField(null=True, blank=True)
    admission_end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False, db_index=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.academic_year_name or ""

class Department(TrackingModel):
    og_code = models.CharField(max_length=50, null=True, blank=True)
    college_id = models.CharField(max_length=50, null=True, blank=True)
    department_code = models.CharField(max_length=50, null=True, blank=True)
    department_name = models.CharField(max_length=255)
    hod_faculty_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    tags = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)


class Semester(TrackingModel):
    semester_number = models.PositiveSmallIntegerField()
    semester_name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)


class ClassGroup(TrackingModel):
    # course_id = models.BigIntegerField(db_index=True)
    semester_ids = models.JSONField(default=list, blank=True)
    class_name = models.CharField(max_length=150)
    division = models.CharField(max_length=30, null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    status = models.BooleanField(default=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)


































class TicketCategory(TrackingModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)



class Rank(TrackingModel):
    # Retained as legacy maritime data. Do not use for college faculty roles.
    department_name = models.IntegerField()
    rank = models.CharField(max_length=255)
    tags = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True)


class Documents(TrackingModel):
    role = models.CharField(max_length=255)
    document_name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=True)


class Languages(TrackingModel):
    languages_name = models.CharField(max_length=255)


class Specialization(TrackingModel):
    specialization_name = models.CharField(max_length=255)


class Branch(TrackingModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    college = models.CharField(max_length=255, null=True, blank=True)
    mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    alternate_mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address_line_one = models.TextField(null=True, blank=True)
    address_line_two = models.TextField(null=True, blank=True)
    country = models.BigIntegerField(null=True, blank=True)
    state = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    landmark = models.CharField(max_length=150, null=True, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)


class Coordinator(TrackingModel):
    branch_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    coordinator_name = models.CharField(max_length=255, null=True)
    coordinator_number = models.CharField(max_length=20, null=True)
    coordinator_email = models.EmailField(null=True)
    coordinator_designation = models.CharField(max_length=255, null=True)


class S3Upload(TrackingModel):
    course = models.JSONField(default=list, blank=True)
    module = models.JSONField(default=list, blank=True)
    s3_tags = models.TextField(default="")
    s3_file = models.TextField(null=True)


class Enquiries(TrackingModel):
    name = models.CharField(max_length=255, null=True)
    contact = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True)
    message = models.TextField(null=True)
    status = models.CharField(max_length=50, null=True)


class Vessel(TrackingModel):
    # Legacy-only model kept so existing migrations/data continue to work.
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    category = models.BigIntegerField(null=True, blank=True)
    subcategory = models.BigIntegerField(null=True, blank=True)
    imo_number = models.CharField(max_length=255, null=True, blank=True)
    mmsi_number = models.CharField(max_length=255, null=True, blank=True)
    flag_state = models.BigIntegerField(null=True, blank=True)
    registry_port = models.CharField(max_length=255, null=True, blank=True)
    built_year = models.DateField(null=True, blank=True)
    shipyard_builder = models.CharField(max_length=255, null=True, blank=True)
    class_society = models.CharField(max_length=255, null=True, blank=True)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    technical_manager = models.CharField(max_length=255, null=True, blank=True)
    commercial_manager = models.CharField(max_length=255, null=True, blank=True)
    operator = models.CharField(max_length=255, null=True, blank=True)
    PI_club = models.CharField(max_length=255, null=True, blank=True)
    last_dry_dock_date = models.DateField(null=True, blank=True)
    next_dry_dock_date = models.DateField(null=True, blank=True)
    last_survey_date = models.DateField(null=True, blank=True)
    next_survey_due_date = models.DateField(null=True, blank=True)
    fuel_consumption_rates = models.TextField(null=True)
    maintenance_history = models.TextField(null=True)
    status = models.BooleanField(default=True)


class EducationalQualifications(TrackingModel):
    qualification_name = models.CharField(max_length=555, null=True, blank=True)
