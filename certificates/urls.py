from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.certificate_request_view, name='request_certificate'),
    path('certificate/<uuid:uuid>/', views.certificate_detail_view, name='certificate_detail'),
    path('certificate/<uuid:uuid>/preview/', views.certificate_preview_view, name='certificate_preview'),
    path('certificate/<uuid:uuid>/download/image/', views.certificate_download_image_view, name='download_image'),
    path('certificate/<uuid:uuid>/download/pdf/', views.certificate_download_pdf_view, name='download_pdf'),
]

