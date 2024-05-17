from django.urls import path
from .views import get_request_count, reset_request_count

urlpatterns = [
    path('request-count/', get_request_count, name='get_request_count'),
    path('request-count/reset/', reset_request_count, name='reset_request_count'),
]