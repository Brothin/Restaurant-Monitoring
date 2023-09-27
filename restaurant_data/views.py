from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StoreStatus
from .generateReport import generate_report  # Import the generate_report function
from .models import Report
from .models import ReportStatus
from celery.result import AsyncResult
from rest_framework.parsers import FileUploadParser
from rest_framework.views import APIView
from rest_framework import status
from .serializers import StoreStatusCSVSerializer, BusinessHoursCSVSerializer, StoreTimezoneCSVSerializer

class UploadStoreStatusCSV(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        csv_file = request.data['status_csv']
        serializer = StoreStatusCSVSerializer(data={'status_csv': csv_file})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadBusinessHoursCSV(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        csv_file = request.data['business_hours_csv']
        serializer = BusinessHoursCSVSerializer(data={'business_hours_csv': csv_file})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UploadStoreTimezoneCSV(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, format=None):
        csv_file = request.data['timezone_csv']
        serializer = StoreTimezoneCSVSerializer(data={'timezone_csv': csv_file})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
def trigger_report(request):
    # Trigger the Celery task
    report_data = generate_report().delay()

    # Create a new Report instance
    report = Report.objects.create()

    # Save the report_data to the Report instance
    report.report_data = report_data

    # Mark the report as complete
    report.status = ReportStatus.COMPLETE
    report.save()

    # Return the report_id as JSON response
    return JsonResponse({"report_id": report.id})

@api_view(['GET'])
def get_report(request, report_id):
    # Check the status of the Celery task using the task ID
    result = AsyncResult(report_id)

    if result.ready():
        # The task is complete, return the report or status
        if result.successful():
            # The task was successful, return the report data
            report_data = result.get()
            return Response({"status": "Complete", "report_data": report_data})
        else:
            # The task failed, return an error message
            return Response({"status": "Error", "message": "Report generation failed"})
    else:
        # The task is still running
        return Response({"status": "Running"})