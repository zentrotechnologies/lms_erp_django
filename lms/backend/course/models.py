from django.db import models
from helpers.models import TrackingModel


class Course(TrackingModel):
    COURSE_TYPE_CHOICES = (
        ("THEORY", "Theory"),
        ("PRACTICAL", "Practical"),
        ("PROJECT", "Project"),
        ("ELECTIVE", "Elective"),
    )

    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    training_mode = models.CharField(max_length=50, null=True, blank=True)
    duration = models.CharField(max_length=100, null=True, blank=True)
    expiry = models.DateField(null=True, blank=True)
    followed_by = models.BigIntegerField(null=True, blank=True)
    topics_covered = models.TextField(default="", blank=True)
    pricing = models.CharField(max_length=12, null=True, blank=True)
    description = models.TextField(default="", blank=True)
    course_status = models.CharField(max_length=50, default="Pending", db_index=True)
    info_status = models.CharField(max_length=50, null=True, blank=True)
    languages = models.JSONField(default=list, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    og_approved = models.BooleanField(default=False)
    og_approvedby = models.CharField(max_length=255, null=True, blank=True)
    ptc_approved = models.BooleanField(default=False)
    ptc_approvedby = models.CharField(max_length=255, null=True, blank=True)

    # College subject mapping
    department_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    program_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    semester_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    academic_year_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    course_type = models.CharField(
        max_length=30, choices=COURSE_TYPE_CHOICES, default="THEORY", db_index=True
    )
    credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_lectures = models.PositiveIntegerField(default=0)
    total_practicals = models.PositiveIntegerField(default=0)

class CourseModules(TrackingModel):
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    module_name = models.TextField(default="")
    module_description = models.TextField(default="")
    module_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sequence_number = models.PositiveIntegerField(default=1)


class CourseMaterial(TrackingModel):
    VISIBILITY_CHOICES = (
        ("ALL", "All"),
        ("FACULTY", "Faculty"),
        ("STUDENT", "Student"),
        ("CLASS", "Specific Class"),
    )

    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    module_id = models.BigIntegerField(null=True, blank=True, db_index=True) #semister
    language = models.BigIntegerField(null=True, blank=True)
    material_type = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    material_label = models.CharField(max_length=255, null=True, blank=True)
    material_link = models.TextField(default="", blank=True)
    material_file = models.TextField(null=True, blank=True)
    class_group_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    uploaded_by = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="CLASS")
    is_published = models.BooleanField(default=False)


class CourseEligibility(TrackingModel):
    # Legacy eligibility model retained; do not use rank-based rules for college flows.
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    category = models.JSONField(default=list, blank=True)
    subcategory = models.JSONField(default=list, blank=True)
    department = models.JSONField(default=list, blank=True)
    rank = models.JSONField(default=list, blank=True)


class rankItemInfo(TrackingModel):
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    eligibilityid = models.BigIntegerField(null=True, blank=True, db_index=True)
    rank = models.BigIntegerField(null=True, blank=True)
    mandatory = models.BooleanField(default=False)


class TrainingMode(TrackingModel):
    training_mode = models.CharField(max_length=255, null=True, blank=True)


class FacultyCourseAllocation(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    faculty_id = models.CharField(max_length=255, db_index=True)
    class_group_id = models.BigIntegerField(db_index=True)
    course_id = models.BigIntegerField(db_index=True)
    allocation_type = models.CharField(max_length=30, default="PRIMARY")
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["academic_year_id", "faculty_id", "class_group_id", "course_id"],
                name="uniq_faculty_course_allocation",
            )
        ]


class LessonPlan(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    department_id = models.BigIntegerField(db_index=True)
    program_id = models.BigIntegerField(db_index=True)
    semester_id = models.BigIntegerField(db_index=True)
    course_id = models.BigIntegerField(db_index=True)
    prepared_by = models.CharField(max_length=255, db_index=True)
    approved_by = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    objectives = models.TextField(null=True, blank=True)
    teaching_methodology = models.TextField(null=True, blank=True)
    references = models.TextField(null=True, blank=True)
    total_planned_lectures = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=30, default="DRAFT", db_index=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_remarks = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class LessonPlanUnit(TrackingModel):
    lesson_plan_id = models.BigIntegerField(db_index=True)
    unit_number = models.PositiveIntegerField()
    unit_title = models.CharField(max_length=255)
    topics = models.TextField()
    planned_lectures = models.PositiveIntegerField(default=0)
    completed_lectures = models.PositiveIntegerField(default=0)
    planned_start_date = models.DateField(null=True, blank=True)
    planned_end_date = models.DateField(null=True, blank=True)
    sequence_number = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["lesson_plan_id", "unit_number"], name="uniq_lesson_plan_unit"
            )
        ]
