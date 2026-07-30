from rest_framework import serializers
from .models import *
from datetime import datetime, time
from master.models import Branch
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
