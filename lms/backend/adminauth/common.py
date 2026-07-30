from datetime import datetime

def convertcreationdate(c_date):
    if c_date is not None and c_date != "" and c_date != "None":
        conv_date = str(c_date).split("T")[0]
        result_date = conv_date.split("-")[2] +"-" + conv_date.split("-")[1] + "-" + conv_date.split("-")[0]
    else:
        result_date = ""
    return result_date

def convertcreationtime(c_date):
    if c_date is not None and c_date != "" and c_date != "None":
        c_date = datetime.fromisoformat(c_date)
        result_time = c_date.strftime('%I:%M:%S %p')
    else:
        result_time = ""
    
    return result_time



def convert_iso_to_human_readable(iso_string):

    try:
        if iso_string is None or iso_string =='':
            return ''
        # Parse the ISO string
        dt = datetime.fromisoformat(iso_string)
        
        # Month abbreviations
        months = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        # Get components
        month = months[dt.month - 1]
        day = dt.day
        year = dt.year
        hour = dt.hour
        minute = dt.minute
        
        # Convert to 12-hour format
        period = 'AM' if hour < 12 else 'PM'
        hour_12 = hour % 12
        if hour_12 == 0:  # 12 AM or 12 PM
            hour_12 = 12
        
        # Format the time with leading zero for minutes
        time_str = f"{hour_12}:{minute:02d} {period}"
        
        # Remove leading zero from day if present
        day_str = str(day)
        
        # Combine all components
        return f"{month} {day_str}, {year} · {time_str}"
    
    except (ValueError, AttributeError, IndexError) as e:
        # Return original string if parsing fails
        print(f"Error converting datetime: {e}")
        return iso_string











