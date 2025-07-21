from .models import RequestLog
from django.utils.timezone import now

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        path = request.path

        RequestLog.objects.create(
            ip_address=ip_address,
            path=path,
            timestamp=now()
        )

        return self.get_response(request)
