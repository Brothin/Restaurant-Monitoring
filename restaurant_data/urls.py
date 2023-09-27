from django.urls import path
from .views import trigger_report, get_report
from django.conf import settings
from django.conf.urls.static import static
import views

urlpatterns = [
    path('trigger_report/', trigger_report, name='trigger_report'),
    path('get_report/<str:report_id>/', get_report, name='get_report'),
    path('upload_store_status_csv/', views.UploadStoreStatusCSV.as_view(), name='upload_store_status_csv'),
    path('upload_business_hours_csv/', views.UploadBusinessHoursCSV.as_view(), name='upload_business_hours_csv'),
    path('upload_store_timezone_csv/', views.UploadStoreTimezoneCSV.as_view(), name='upload_store_timezone_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)