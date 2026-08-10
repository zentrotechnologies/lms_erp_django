from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import jwt
import uuid

from helpers.models import TrackingModel


class CandidateManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)


class Candidate(AbstractBaseUser, TrackingModel):
    ADMISSION_STATUS_CHOICES = (
        ("APPLIED", "Applied"),
        ("PROVISIONAL", "Provisional"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("ALUMNI", "Alumni"),
    )
    STUDENT_STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("SUSPENDED", "Suspended"),
        ("COMPLETED", "Completed"),
        ("DROPPED", "Dropped"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_pic = models.TextField(null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(_("email address"), null=True, blank=False, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=10, null=True, blank=True)
    mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    alternate_mobilenumber = models.CharField(max_length=20, null=True, blank=True)
    highest_qualification = models.CharField(max_length=255, null=True, blank=True)
    qualification_year = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

    # Legacy Navy fields retained only for migration/backward compatibility.
    passport_expiry_date = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    vessel_name = models.CharField(max_length=150, null=True, blank=True)
    next_vessel = models.CharField(max_length=150, null=True, blank=True)
    sign_on_date = models.DateField(null=True, blank=True)
    sign_of_date = models.DateField(null=True, blank=True)
    seaman_book_number = models.CharField(max_length=255, null=True, blank=True)
    rank = models.CharField(max_length=255, null=True, blank=True)
    coc = models.CharField(max_length=255, null=True, blank=True)

    country = models.BigIntegerField(null=True, blank=True, db_index=True)
    state = models.BigIntegerField(null=True, blank=True, db_index=True)
    city = models.CharField(max_length=150, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)
    address_line_one = models.TextField(null=True, blank=True)
    address_line_two = models.TextField(null=True, blank=True)

    department = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)
    candidate_status = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    action_takenby = models.CharField(max_length=255, null=True, blank=True)
    action_takenby_user_type = models.BigIntegerField(null=True, blank=True)
    application_number = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    decline_reason = models.TextField(null=True, blank=True)
    certificate_name = models.CharField(max_length=255, null=True, blank=True)
    educational_certificate = models.TextField(null=True, blank=True)
    deleted_by = models.CharField(max_length=255, null=True, blank=True)
    walkin_by = models.CharField(max_length=255, null=True, blank=True)

    # College student fields. UUID-linked records are stored as strings.
    university_prn = models.CharField(max_length=100, null=True, blank=True, unique=True)
    mentor_faculty_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)



    admission_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    roll_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    academic_year_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    college_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    role_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
    )

    department_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    program_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    semester_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    class_group_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    division = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    admission_date = models.DateField(
        null=True,
        blank=True,
    )

    admission_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Draft",
        db_index=True,
    )

    student_status = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="Active",
        db_index=True,
    )

    mother_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    gender = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    blood_group = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    marital_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    place_of_birth = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    religion = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    caste = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    category = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    mother_tongue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    domicile_state = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    is_minority = models.BooleanField(default=False)

    is_handicapped = models.BooleanField(default=False)

    aadhaar_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    abc_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    local_address = models.TextField(
        null=True,
        blank=True,
    )

    local_city = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    local_state = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    local_pincode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )








    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CandidateManager()

    @property
    def token(self):
        return jwt.encode(
            {"id": self.id.hex, "createdAt": timezone.now().isoformat()},
            settings.SECRET_KEY,
            algorithm="HS256",
        )


class ParentProfile(TrackingModel):
    parent_code = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True, db_index=True)
    mobile = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_relationship = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )



    parent_annual_income = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    parent_government_employee = models.BooleanField(default=False)

class ParentStudentMapping(TrackingModel):
    parent_id = models.BigIntegerField(db_index=True)
    student_id = models.CharField(max_length=255, db_index=True)
    relationship = models.CharField(max_length=30)
    is_primary = models.BooleanField(default=False)
    can_receive_notifications = models.BooleanField(default=True)
    can_view_marks = models.BooleanField(default=True)
    can_view_attendance = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["parent_id", "student_id", "relationship"],
                name="uniq_parent_student_relation",
            )
        ]


class candidatelog(TrackingModel):
    candidate_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    action_takenbyid = models.CharField(max_length=255, null=True, blank=True)
    action_usertype = models.BigIntegerField(null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    decline_reason = models.TextField(null=True, blank=True)


class CandidateToken(TrackingModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    authToken = models.TextField(null=True, blank=True)
    apptoken = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=50, null=True, blank=True)


class CandidateDocuments(TrackingModel):
    user_id = models.CharField(max_length=255, null=True, db_index=True)
    document_id = models.IntegerField(null=True, db_index=True)
    document_name = models.CharField(max_length=255, null=True)
    document_url = models.TextField(null=True)
    status = models.BooleanField(default=False)
    reject_reason = models.TextField(null=True)
    application_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    document_type = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    verified_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

class candidateOtp(TrackingModel):
    candidate = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobileotp = models.CharField(max_length=10, null=True, blank=True)
    emailotp = models.CharField(max_length=10, null=True, blank=True)
class AdmissionApplication(TrackingModel):
    candidate_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    application_number = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )

    academic_year_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    program_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    class_group_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    admission_applying_for = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    admission_applying_class = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    personal_info_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    educational_info_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    photo_signature_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    subject_selection_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    payment_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    submission_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    verification_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    admission_confirmation_status = models.CharField(
        max_length=50,
        default="Pending",
    )

    current_step = models.CharField(
        max_length=100,
        default="PERSONAL_INFO",
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    verified_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rejection_reason = models.TextField(
        null=True,
        blank=True,
    )

class CandidateEducation(TrackingModel):
    candidate_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    application_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    previous_exam_passed = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    qualification = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    board_university = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    institute_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    passing_year = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    seat_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

    percentage = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    cgpa = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    eligibility_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )

class CandidatePhotoSignature(TrackingModel):
    candidate_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    application_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
    )

    photo_url = models.TextField(
        null=True,
        blank=True,
    )

    signature_url = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=50,
        default="Pending",
    )