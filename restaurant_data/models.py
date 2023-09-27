from django.db import models
from django.contrib.postgres.fields import JSONField

class StoreStatus(models.Model):
    store_id = models.IntegerField()
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)  # 'active' or 'inactive'
    status_csv = models.FileField(upload_to='store_status_csv/')

class BusinessHours(models.Model):
    store_id = models.IntegerField()
    day_of_week = models.IntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()
    business_hours_csv = models.FileField(upload_to='business_hours_csv/')

class StoreTimezone(models.Model):
    store_id = models.IntegerField()
    timezone_str = models.CharField(max_length=50)
    timezone_csv = models.FileField(upload_to='timezone_csv/')

class ReportStatus(models.TextChoices):
    PENDING = 'Pending'
    COMPLETE = 'Complete'

class Report(models.Model):
    store_id = models.IntegerField()
    uptime_last_hour = models.IntegerField()
    uptime_last_day = models.FloatField()
    uptime_last_week = models.FloatField()
    downtime_last_hour = models.IntegerField()
    downtime_last_day = models.FloatField()
    downtime_last_week = models.FloatField()

class AsyncResultModel(models.Model):
    task_id = models.CharField(max_length=255, unique=True)  # Store the task ID as a unique identifier
    status = models.CharField(max_length=50)  # Status of the Celery task (e.g., "PENDING", "SUCCESS", "FAILURE")
    result = models.JSONField(blank=True, null=True)  # Store the result data as JSON

    def __str__(self):
        return f"Task ID: {self.task_id}, Status: {self.status}"