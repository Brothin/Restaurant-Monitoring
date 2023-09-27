from rest_framework import serializers
from .models import StoreStatus, BusinessHours, StoreTimezone
from .models import Report, ReportStatus, AsyncResultModel

class StoreStatusCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreStatus
        fields = ('status_csv',)

class BusinessHoursCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessHours
        fields = ('business_hours_csv',)

class StoreTimezoneCSVSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTimezone
        fields = ('timezone_csv',)

class ReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportStatus
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class AsyncResultModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsyncResultModel
        fields = '__all__'