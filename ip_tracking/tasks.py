# ip_tracking/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ip_tracking.models import SuspiciousIP
from django.core.cache import cache

SENSITIVE_PATHS = ['/admin', '/login']

@shared_task
def detect_anomalies():
    now = timezone.now()
    one_hour_ago = now - timedelta(hours=1)

    # Simulate IP request logs; replace with actual logic in production
    request_logs = cache.get('request_logs', {})

    for ip, entries in request_logs.items():
        request_count = len([e for e in entries if e['timestamp'] > one_hour_ago])

        if request_count > 100:
            SuspiciousIP.objects.get_or_create(ip_address=ip, reason="High request rate")
        else:
            for entry in entries:
                if entry['path'] in SENSITIVE_PATHS:
                    SuspiciousIP.objects.get_or_create(ip_address=ip, reason="Accessed sensitive path")
