#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from collectorapp.models import CollectorProfile

collector = CollectorProfile.objects.filter(is_verified=False).order_by('-user__date_joined').first()
if not collector:
    print('No unverified collector accounts found.')
    exit(0)

user = collector.user
print(f'Verifying collector: username={user.username}, email={user.email}, token={collector.verification_token}')
collector.is_verified = True
collector.save()
user.is_active = True
user.save()
print('Collector marked verified and user activated.')
