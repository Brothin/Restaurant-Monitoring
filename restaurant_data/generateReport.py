# restaurant_data/tasks.py
from celery import shared_task
from .models import StoreStatus, BusinessHours, StoreTimezone
from datetime import datetime, timedelta
from pytz import timezone
from .models import Report

@shared_task
def generate_report():
    # Get the current timestamp (max timestamp among all observations in CSV 1)
    current_time_utc = datetime.now().replace(tzinfo=timezone('UTC'))

    # Iterate through stores
    for store in StoreStatus.objects.values('store_id').distinct():
        store_id = store['store_id']
        store_timezones = StoreTimezone.objects.filter(store_id=store_id)
        
        # Use 'America/Chicago' as default timezone if not found
        if not store_timezones.exists():
            store_timezone = timezone('America/Chicago')
        else:
            store_timezone = timezone(store_timezones.first().timezone_str)

        # Retrieve business hours for the store
        business_hours = BusinessHours.objects.filter(store_id=store_id)

        # Initialize report data for the store
        report_data = {
            'store_id': store_id,
            'uptime_last_hour': 0,
            'uptime_last_day': 0,
            'uptime_last_week': 0,
            'downtime_last_hour': 0,
            'downtime_last_day': 0,
            'downtime_last_week': 0
        }

        # Calculate the time intervals for the last hour, last day, and last week
        last_hour = current_time_utc - timedelta(hours=1)
        last_day = current_time_utc - timedelta(days=1)
        last_week = current_time_utc - timedelta(weeks=1)

        # Loop through each business day and calculate uptime and downtime
        for day in range(7):
            business_day_hours = business_hours.filter(day_of_week=day)
            
            # If no business hours data is found, assume it's open 24/7
            if not business_day_hours.exists():
                business_day_hours = [{'start_time_local': datetime.min.time(), 'end_time_local': datetime.max.time()}]

            for business_hours_entry in business_day_hours:
                start_time_local = business_hours_entry['start_time_local']
                end_time_local = business_hours_entry['end_time_local']
                start_time_utc = store_timezone.localize(datetime.combine(current_time_utc.date(), start_time_local))
                end_time_utc = store_timezone.localize(datetime.combine(current_time_utc.date(), end_time_local))

                # Calculate uptime and downtime for each time interval
                status_entries = StoreStatus.objects.filter(
                    store_id=store_id,
                    timestamp_utc__gte=start_time_utc,
                    timestamp_utc__lte=end_time_utc
                )

                # Calculate uptime and downtime for the last hour
                report_data['uptime_last_hour'] += calculate_uptime(last_hour, status_entries)
                report_data['downtime_last_hour'] += calculate_downtime(last_hour, status_entries)

                # Calculate uptime and downtime for the last day
                report_data['uptime_last_day'] += calculate_uptime(last_day, status_entries)
                report_data['downtime_last_day'] += calculate_downtime(last_day, status_entries)

                # Calculate uptime and downtime for the last week
                report_data['uptime_last_week'] += calculate_uptime(last_week, status_entries)
                report_data['downtime_last_week'] += calculate_downtime(last_week, status_entries)

        # Create a new report instance and save it to the database
    report_instance = Report(
        store_id=store_id,
        uptime_last_hour=report_data['uptime_last_hour'],
        uptime_last_day=report_data['uptime_last_day'],
        uptime_last_week=report_data['uptime_last_week'],
        downtime_last_hour=report_data['downtime_last_hour'],
        downtime_last_day=report_data['downtime_last_day'],
        downtime_last_week=report_data['downtime_last_week']
    )
    report_instance.save()

def calculate_uptime(time_interval, status_entries):
    uptime_minutes = 0
    
    # Sort status_entries by timestamp_utc to ensure they are in chronological order
    sorted_entries = status_entries.order_by('timestamp_utc')

    # Initialize the previous status as 'inactive' (0) for the start of the interval
    prev_status = 0

    for entry in sorted_entries:
        timestamp_utc = entry.timestamp_utc

        # Check if the timestamp is within the specified time interval
        if timestamp_utc >= time_interval:
            break

        # Calculate the time difference between the current and previous entry
        time_diff = (timestamp_utc - time_interval).total_seconds() / 60

        # If the status changed from 'inactive' (0) to 'active' (1), add the time_diff to uptime
        if entry.status == 'active' and prev_status == 0:
            uptime_minutes += time_diff

        prev_status = 1 if entry.status == 'active' else 0

    return uptime_minutes

def calculate_downtime(time_interval, status_entries):
    downtime_minutes = 0
    
    # Sort status_entries by timestamp_utc to ensure they are in chronological order
    sorted_entries = status_entries.order_by('timestamp_utc')

    # Initialize the previous status as 'active' (1) for the start of the interval
    prev_status = 1

    for entry in sorted_entries:
        timestamp_utc = entry.timestamp_utc

        # Check if the timestamp is within the specified time interval
        if timestamp_utc >= time_interval:
            break

        # Calculate the time difference between the current and previous entry
        time_diff = (timestamp_utc - time_interval).total_seconds() / 60

        # If the status changed from 'active' (1) to 'inactive' (0), add the time_diff to downtime
        if entry.status == 'inactive' and prev_status == 1:
            downtime_minutes += time_diff

        prev_status = 0 if entry.status == 'inactive' else 1

    return downtime_minutes