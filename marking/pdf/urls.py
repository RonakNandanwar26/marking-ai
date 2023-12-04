from django.urls import path
from .views import *


urlpatterns = [
    path('upload_pdf/',UploadPDF.as_view(),name='upload_pdf_api'),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
]