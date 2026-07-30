from rest_framework import serializers
from .models import *
from datetime import datetime, time
from master.models import Branch
from django.utils.timezone import now
import os
class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields ="__all__"
class TicketAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAssign
        fields ="__all__"
class FAQTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQTicket
        fields ="__all__"

class CustomTicketAssignSerializer(serializers.ModelSerializer):
    # createdAt_formatted = serializers.SerializerMethodField()

    class Meta:
        model = TicketAssign
        fields ="__all__"
        
    # def get_createdAt_formatted(self, obj):
    #     if obj.createdAt:

    #         return obj.createdAt.strftime("%b %d, %Y · %I:%M %p")  # Jan 14, 2025 · 10:00 AM format
    #     return None
    

class TicketActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketActivity
        fields ="__all__"
class CustomTicketActivitySerializer(serializers.ModelSerializer):

    createdAt_formatted = serializers.SerializerMethodField()
    time_difference = serializers.SerializerMethodField()
    
    file_name = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()

    def get_createdAt_formatted(self, obj):
        if obj.createdAt:
            return obj.createdAt.strftime("%b %d, %Y · %I:%M %p")  # Jan 14, 2025 · 10:00 AM format
        return None
    def get_file_name(self, obj):
        if str(obj.attachment) is not None and str(obj.attachment) !='':
            filename, file_extension = os.path.splitext(os.path.basename(str(obj.attachment)))
            return filename
        else:
            return 'NA'
        

    def get_file_extension(self, obj):
        if str(obj.attachment) is not None and str(obj.attachment) !='':
            filename, file_extension = os.path.splitext(os.path.basename(str(obj.attachment)))
            return file_extension
        else:
            return 'NA'

    class Meta:
        model = TicketActivity
        fields ="__all__"

    def get_time_difference(self, obj):
        if obj.createdAt:
            time_diff = now() - obj.createdAt  # Using Django's timezone-aware `now()`
            days = time_diff.days
            hours, remainder = divmod(time_diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Formatting output based on time difference
            if days > 0:
                return f"{days} day{'s' if days > 1 else ''} ago"
            elif hours > 0:
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif minutes > 0:
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        return None

class CustomTicketAttachmentsSerializer(serializers.ModelSerializer):
    createdAt_formatted = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachments
        fields ="__all__"



    def get_createdAt_formatted(self, obj):
        if obj.createdAt:
            return obj.createdAt.strftime("%b %d, %Y · %I:%M %p")  # Jan 14, 2025 · 10:00 AM format
        return None



class TicketAttachmentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketAttachments
        fields ="__all__"
