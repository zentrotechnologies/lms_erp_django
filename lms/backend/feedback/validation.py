from datetime import datetime
from lms.settings import *


def datefilterchangeformat(df):
    
    x = datetime.strptime(df, '%Y-%m-%d')
    changeformat = x.strftime('%d %b %Y')
    return changeformat

def timefilterchangeformat(tf):
    time_12 = datetime.strptime(tf, "%H:%M:%S").strftime("%I:%M %p")
    return time_12

# # Example Usage
# iso_timestamp = "2025-02-05"
# formatted_time = format_timestamp(iso_timestamp)

# Example Usage
# iso_timestamp = "2025-07-15T00:24:07.123Z"
# formatted_time = format_timestamp(iso_timestamp)
