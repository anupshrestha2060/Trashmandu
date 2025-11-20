#!/usr/bin/env python
"""
Force resend collector verification email for the most recent unverified collector.
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from collectorapp.models import CollectorProfile
from django.core.mail import send_mail
from django.conf import settings

# Find the most recent unverified collector
collector = CollectorProfile.objects.filter(is_verified=False).order_by('-user__date_joined').first()
if not collector:
    print('No unverified collector found.')
    exit(0)

user = collector.user
site_url = getattr(settings, 'SITE_URL', None) or 'http://127.0.0.1:8000'
verification_link = f"{site_url.rstrip('/')}/collector/verify/{collector.verification_token}/"
subject = 'Trashmandu - Verify your collector account'
message = f"Hi {user.first_name},\n\nThis is a re-send. Click this link to verify your collector account:\n{verification_link}\n\nIf you already verified, ignore this message.\n\nBest regards,\nTrashmandu Team"
from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@trashmandu.com')

print(f"Forcing resend to: {user.email} (username: {user.username})")
try:
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
    print('send_mail() executed.')
except Exception as e:
    print('Error sending email:', e)

# If file backend, print the most recent file
sent_dir = Path(getattr(settings, 'EMAIL_FILE_PATH', Path(settings.BASE_DIR) / 'sent_emails'))
if sent_dir.exists():
    latest = sorted(sent_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True)
    if latest:
        print('Latest sent_emails file:')
        print(' -', latest[0])
        # print a short preview
        try:
            txt = latest[0].read_text(encoding='utf-8', errors='ignore')
            print('\n--- Email preview (first 400 chars) ---')
            print(txt[:400])
        except Exception as e:
            print('Could not read file:', e)
else:
    print('Email file directory does not exist; maybe SMTP backend is used.')
