#!/usr/bin/env python
"""Test: send collector notification for the most recent unverified user

This script finds the most recently created unverified `UserProfile` and
sends notification emails to all verified collectors using the same code
we added to `user_register`.
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from userapp.models import UserProfile
from collectorapp.models import CollectorProfile
from django.core.mail import send_mail

# Find latest unverified user profile
profile = UserProfile.objects.filter(is_verified=False).order_by('-id').first()
if not profile:
    print('No unverified user profiles found.')
    exit(0)

user = profile.user
print(f'Found unverified user: {user.username} <{user.email}>')

collector_emails = list(CollectorProfile.objects.filter(is_verified=True).values_list('user__email', flat=True))
collector_emails = [e for e in set(collector_emails) if e and e != user.email]

if not collector_emails:
    print('No verified collectors to notify.')
    exit(0)

subject = 'Trashmandu - New user registered'
message = f"A new user has registered: {user.first_name} ({user.username})\n\nCheck your collector dashboard to view pickup requests.\n\nBest regards,\nTrashmandu Team"
from_email = settings.DEFAULT_FROM_EMAIL

send_mail(subject, message, from_email, [], bcc=collector_emails, fail_silently=False)
print('Notification sent (file backend will write to sent_emails/).')
