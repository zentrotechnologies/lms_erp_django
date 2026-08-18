from lms.settings import *
import psycopg2
from psycopg2.extras import RealDictCursor
from uuid import UUID
from datetime import datetime, date


hostURL = "http://127.0.0.1:8000"
frontURL = "http://127.0.0.1:8002"
candidateURL = "http://127.0.0.1:8002"
collegeURL = "http://127.0.0.1:8001"



queryconn = psycopg2.connect(database=env('DATABASE_NAME'), user= env('DATABASE_USER'),password=env('DATABASE_PASSWORD'), host=env('DATABASE_HOST'), port=env('DATABASE_PORT'), cursor_factory=RealDictCursor)



#encryprion
from cryptography.fernet import Fernet
from decimal import Decimal
from django.conf import settings
import json
from rest_framework.response import Response
from datetime import datetime
from django.db.models import QuerySet

def handle_request_body(request):
    try:
        if request.content_type == 'application/x-www-form-urlencoded' or request.content_type == "application/x-www-form-urlencoded; charset=UTF-8":
            request_data = request.POST
        elif request.content_type.startswith('multipart/form-data'):
            # Handle form fields and file uploads
            request_data = request.POST  # Text fields
            request_files = request.FILES  # File uploads
        else:
            raw_data = request.body.decode('utf-8')
            try:
                request_data = json.loads(decrypt_data(raw_data))
            except Exception:
                request_data = json.loads(raw_data)
    except json.JSONDecodeError:
        return None, Response({"status": "failed", "msg": "Invalid JSON format"}, status=400)

    return request_data, None


def convert_decimals_to_float(data):
    if isinstance(data, dict):
        return {key: convert_decimals_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_decimals_to_float(item) for item in data]
    elif isinstance(data, set):
        return list(data)  
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, QuerySet):
        return list(data)
    elif isinstance(data, UUID):         
        return str(data)
    return data

base_encryption_key = b'D3KyP1sPstZZa4Yf2u0E0unfXgR9L5s2iIpoU-W5_Yc='


def encrypt_data(data):
    cipher_suite = Fernet(base_encryption_key)
    if isinstance(data, str):
        data = data.encode()
    encrypted_data = cipher_suite.encrypt(data)
    return encrypted_data.decode()

def decrypt_data(encrypted_data):
    cipher_suite = Fernet(base_encryption_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
    return decrypted_data.decode()

from datetime import datetime

def datefilterchangeformat(df):
    
    x = datetime.strptime(df, '%Y-%m-%d')
    changeformat = x.strftime('%d %b %Y')
    return changeformat


def datefiltergetyear(df):
    x = datetime.strptime(df, '%Y-%m-%d')
    newformat = x.strftime('%Y')
    return newformat


def convertdate(date):
    date_str = str(date)
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d %B, %Y")
    return formatted_date

def convertdatewithtime(date):
    date_str = str(date)
    date_obj = datetime.fromisoformat(date_str)
    formatted_date = date_obj.strftime("%d %B, %Y %H:%M:%S")
    return formatted_date

def gettimediff(starttime,enddtime):
    starttime = datetime.fromisoformat(starttime)
    endtime = datetime.fromisoformat(enddtime)

    # Calculate time difference
    delta = endtime - starttime

    # Get total seconds and format as H:M:S
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_time

# import pytz
def getdatewithtime(dt_str):
    dt = datetime.fromisoformat(dt_str)
    day = dt.day
    suffix = 'th' if 11 <= day <= 13 else {1:'st', 2:'nd', 3:'rd'}.get(day % 10, 'th')
    formatted_date = dt.strftime(f"%d{suffix} %B, %Y %I:%M %p")
    return formatted_date

def getdays(dt_str):
    today = date.today() 
    expiry_date = datetime.strptime(dt_str, '%Y-%m-%d').date()  
    days_remaining = (expiry_date - today).days
    return days_remaining






from rest_framework import pagination
class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'p'

    def get_paginated_response(self,data):
        response = {
            'count':self.page.paginator.count,
            'next' : self.get_next_link(),
            'previous' : self.get_previous_link(),
            'data':data,
            "msg": 'data found successfully',
            "n": 1,
        }
     
        return response
    



