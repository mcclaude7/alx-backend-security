from .models import RequestLog, BlockedIP
from django.http import HttpResponseForbidden
import requests
from django.core.cache import cache
from ipware import get_client_ip
from .models import RequestLog
from django.utils.timezone import now
from django.core.cache import cache

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = request.META.get('REMOTE_ADDR')
        path = request.path
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        RequestLog.objects.create(
            ip_address=ip_address,
            path=request.path,
            timestamp=now()
        )

        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
    
class IPGeolocationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)
        country, city = None, None

        if ip:
            cache_key = f"geo_{ip}"
            geo_data = cache.get(cache_key)

            if not geo_data:
                # Replace with your API and API key
                API_KEY = "44a1861ba056402da1eb59c91e1cc284"
                url = f"https://api.ipgeolocation.io/ipgeo?apiKey={API_KEY}&ip={ip}"

                try:
                    resp = requests.get(url, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        country = data.get("country_name")
                        city = data.get("city")
                        geo_data = {"country": country, "city": city}
                        cache.set(cache_key, geo_data, 24 * 3600)  # cache for 24 hours
                except requests.RequestException:
                    pass
            else:
                country = geo_data.get("country")
                city = geo_data.get("city")

            # Save the RequestLog (you can customize what else to save)
            RequestLog.objects.create(ip_address=ip, country=country, city=city)

        response = self.get_response(request)
        return response
class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        path = request.path
        timestamp = now()

        logs = cache.get('request_logs', {})
        if ip not in logs:
            logs[ip] = []

        logs[ip].append({'path': path, 'timestamp': timestamp})
        cache.set('request_logs', logs, timeout=3600)

        return self.get_response(request)

