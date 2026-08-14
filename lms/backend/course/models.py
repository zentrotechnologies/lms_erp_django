from django.db import models
from helpers.models import TrackingModel

class Subject(TrackingModel):
    SUBJECT_TYPE_CHOICES = (
        ("THEORY", "Theory"),
        ("PRACTICAL", "Practical"),
        ("THEORY_PRACTICAL", "Theory + Practical"),
        ("PROJECT", "Project"),
        ("ELECTIVE", "Elective"),
        ("LAB", "Lab"),
    )

    subject_code = models.CharField(max_length=100, db_index=True)
    subject_name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=100, null=True, blank=True)

    department_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    subject_type = models.CharField(
        max_length=30,
        choices=SUBJECT_TYPE_CHOICES,
        default="THEORY",
        db_index=True,
    )

    theory_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_credits = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    theory_marks = models.PositiveIntegerField(default=0)
    practical_marks = models.PositiveIntegerField(default=0)
    internal_marks = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)

    description = models.TextField(null=True, blank=True)
    status = models.BooleanField(default=True, db_index=True)



    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

class Course(TrackingModel):
    COURSE_TYPE_CHOICES = (
        ("THEORY", "Theory"),
        ("PRACTICAL", "Practical"),
        ("PROJECT", "Project"),
        ("ELECTIVE", "Elective"),
        ("THEORY+PRACTICAL", "Theory+Practical"),
    )

    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    pricing = models.CharField(max_length=12, null=True, blank=True)
    description = models.TextField(default="", blank=True)
    course_status = models.CharField(max_length=50, default='Pending')
    languages = models.JSONField(default=list, blank=True)
    og_code = models.CharField(max_length=150, null=True, blank=True)
    og_approved = models.BooleanField(default=False)
    og_approvedby = models.CharField(max_length=255, null=True, blank=True)
    ptc_approved = models.BooleanField(default=False)
    ptc_approvedby = models.CharField(max_length=255, null=True, blank=True)
    # College subject mapping
    department_id = models.BigIntegerField(null=True, blank=True, db_index=True)

    category_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    sub_category_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    course_type = models.CharField( max_length=30, choices=COURSE_TYPE_CHOICES, default="THEORY", db_index=True    )
    total_lectures = models.PositiveIntegerField(default=0)
    total_practicals = models.PositiveIntegerField(default=0)
    semister_count = models.BigIntegerField(null=True, blank=True, db_index=True)
    semister_per_year = models.BigIntegerField(null=True, blank=True, db_index=True)
    duration = models.CharField(max_length=100, null=True, blank=True)

class CourseSubjects(TrackingModel):
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    semister_no = models.BigIntegerField(null=True, blank=True, db_index=True)
    subject_id = models.BigIntegerField(null=True, blank=True, db_index=True)


class CourseClass(TrackingModel):
    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    class_id = models.BigIntegerField(null=True, blank=True, db_index=True)















class CourseMaterial(TrackingModel):
    VISIBILITY_CHOICES = (
        ("ALL", "All"),
        ("FACULTY", "Faculty"),
        ("STUDENT", "Student"),
        ("CLASS", "Specific Class"),
    )

    course_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    subject_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    language = models.BigIntegerField(null=True, blank=True)
    material_type = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    material_label = models.CharField(max_length=255, null=True, blank=True)
    material_link = models.TextField(default="", blank=True)
    material_file = models.TextField(null=True, blank=True)
    semister_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    uploaded_by = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="CLASS")
    is_published = models.BooleanField(default=False)

class FacultyCourseAllocation(TrackingModel):
    academic_year_id = models.BigIntegerField(db_index=True)
    faculty_id = models.CharField(max_length=255, db_index=True)
    course_id = models.BigIntegerField(db_index=True)
    subject_id = models.BigIntegerField(db_index=True)













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


