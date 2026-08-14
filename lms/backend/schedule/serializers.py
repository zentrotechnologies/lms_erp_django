from rest_framework import serializers
from .models import *
from datetime import datetime, time
from master.models import Branch, ClassGroup, Semester
from course.models import *
from adminauth.models import UserAdmin

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields ="__all__"

class CustomScheduleSerializer(serializers.ModelSerializer):
    course_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())
    training_center_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Course.objects.all())
    course_names = serializers.SerializerMethodField()
    training_center_names = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    formatted_start_date = serializers.SerializerMethodField()
    formatted_end_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()
    faculty_name = serializers.SerializerMethodField()


    class Meta:
        model = Schedule
        fields ="__all__"
    
    def get_course_names(self, obj):
        # Fetch all related courses and return their names
        return [course.course_name for course in obj.course_ids.all()]
    
    def get_training_center_names(self, obj):
        # Fetch all related courses and return their names
        return [course.name for course in obj.training_center_ids.all()]
    
    def get_branch_name(self, obj):
        obj_id = obj.branch_id
        if obj_id:
            obj = Branch.objects.filter(id=obj_id,isActive=True).first()
            if obj is not None and obj !='':
                return obj.name
            else:
                return None
        else:
            return None
    
    def get_faculty_name(self, obj):
        obj_id = str(obj.faculty_id)
        if obj_id:
            obj = UserAdmin.objects.filter(id=obj_id,isActive=True).first()
            if obj is not None and obj !='':
                return str(obj.first_name)+ ' ' +str(obj.last_name)
            else:
                return None
        else:
            return None

    def get_status(self, obj):
        now = datetime.now()

        # Check if dates and times are set
        if obj.start_date and obj.end_date:
            if obj.start_date > now.date():
                return "Upcoming"
            elif obj.end_date < now.date():
                return "Completed"
            elif obj.start_date <= now.date() <= obj.end_date:
                # Check time if the current date is within the schedule range
                if obj.start_time and obj.end_time:
                    try:
                        start_time = datetime.strptime(obj.start_time, "%H:%M").time()
                        end_time = datetime.strptime(obj.end_time, "%H:%M").time()

                        if start_time <= now.time() <= end_time:
                            return "Ongoing"
                        elif now.time() < start_time:
                            return "Upcoming"
                        else:
                            return "Completed"
                    except ValueError:
                        return "Invalid Time Format"
                return "Ongoing"
        return "No Schedule"

    def get_formatted_start_date(self, obj):
        if obj.start_date:
            return obj.start_date.strftime("%d %B, %Y")  # Format: 21 July, 2024
        return None

    def get_formatted_end_date(self, obj):
        if obj.end_date:
            return obj.end_date.strftime("%d %B, %Y")  # Format: 21 July, 2024
        return None

    def get_formatted_time(self, obj):
        if obj.start_time and obj.end_time:
            try:
                # Parse and format start and end times
                start_time = datetime.strptime(obj.start_time, "%H:%M").strftime("%I:%M %p")
                end_time = datetime.strptime(obj.end_time, "%H:%M").strftime("%I:%M %p")
                return f"{start_time} - {end_time}"
            except ValueError:
                return "Invalid Time Format"
        return None


class RescheduleLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RescheduleLog
        fields ="__all__"

class UniqueScheduleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    schedulename = serializers.CharField()
    training_center_id = serializers.IntegerField()
    training_center_name = serializers.CharField()
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    formatted_start_date = serializers.CharField()
    formatted_end_date = serializers.CharField()
    formatted_time = serializers.CharField()
    mode = serializers.CharField()
    branch_name = serializers.CharField()

    @classmethod
    def get_unique_pairs(cls, queryset):
        """Transforms queryset into unique training_center_id & course_id pairs with names"""
        unique_schedules = []
        seen_pairs = set()

        for schedule in queryset:
            training_centers = schedule.training_center_ids.all()
            courses = schedule.course_ids.all()

            for training_center in training_centers:
                for course in courses:
                    pair = (training_center.id, course.id)

                    if pair not in seen_pairs:
                        seen_pairs.add(pair)
                        unique_schedules.append({
                            "id": schedule.id,
                            "schedulename": schedule.schedulename,
                            "training_center_id": training_center.id,
                            "training_center_name": training_center.name,
                            "course_id": course.id,
                            "course_name": course.course_name
                        })

        return unique_schedules


class TimetableTemplateListSerializer(serializers.ModelSerializer):
    """List serializer for TimetableTemplate.

    All lookups are resolved in bulk by the view and passed via ``context``:
    ``class_group_map``, ``semester_map``, ``user_map`` and ``slot_count_map``.
    This removes the per-template N+1 queries.
    """
    class_name = serializers.SerializerMethodField()
    semister = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    total_lectures = serializers.SerializerMethodField()

    class Meta:
        model = TimetableTemplate
        fields = ['id', 'template_name', 'class_name', 'semister', 'total_lectures', 'created_by_name', 'created_date']

    def get_class_name(self, obj):
        """Get class name from ClassGroup"""
        class_group = self.context.get('class_group_map', {}).get(obj.class_group_id)
        if class_group:
            return f"{class_group.class_name} {class_group.division or ''}".strip()
        return ""

    def get_semister(self, obj):
        """Get semester name from ClassGroup -> Semester"""
        class_group = self.context.get('class_group_map', {}).get(obj.class_group_id)
        if class_group and class_group.semester_id:
            semester = self.context.get('semester_map', {}).get(class_group.semester_id)
            if semester:
                return semester.semester_name
        return ""

    def get_created_by_name(self, obj):
        """Get creator's name from createdBy field"""
        creator_id = obj.created_by or obj.createdBy
        if creator_id:
            user = self.context.get('user_map', {}).get(str(creator_id))
            if user:
                if user.user_type == 5:  # Faculty
                    return f"{user.first_name or ''} {user.last_name or ''}".strip()
                return user.name or f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or ""
        return ""

    def get_created_date(self, obj):
        """Format created date"""
        if obj.createdAt:
            return obj.createdAt.strftime("%d/%m/%Y")
        return ""

    def get_total_lectures(self, obj):
        """Count total lecture slots for this template"""
        return self.context.get('slot_count_map', {}).get(obj.id, 0)
