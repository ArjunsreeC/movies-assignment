from django.http import JsonResponse
from .middleware import RequestCountMiddleware

def get_request_count(request):
    count = RequestCountMiddleware.get_request_count()
    return JsonResponse({"requests": count})

def reset_request_count(request):
    RequestCountMiddleware.reset_request_count()
    return JsonResponse({"message": "request count reset successfully"})