from threading import Lock

class RequestCountMiddleware:
    request_count = 0
    lock = Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        with self.lock:
            RequestCountMiddleware.request_count += 1
        response = self.get_response(request)
        return response

    @classmethod
    def get_request_count(cls):
        with cls.lock:
            return cls.request_count

    @classmethod
    def reset_request_count(cls):
        with cls.lock:
            cls.request_count = 0
