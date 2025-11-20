#!/usr/bin/env python
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from collectorapp.models import CollectorProfile
from django.core.mail import send_mail
from django.conf import settings

sent_dir = Path(getattr(settings, 'EMAIL_FILE_PATH', Path(settings.BASE_DIR) / 'sent_emails'))

unverified = CollectorProfile.objects.filter(is_verified=False).order_by('-user__date_joined')
if not unverified.exists():
    print('No unverified collector accounts found.')
    exit(0)

collector = unverified.first()
user = collector.user
print(f"Found unverified collector: username={user.username}, email={user.email}, token={collector.verification_token}")

# Search sent_emails for the token
token_str = f"/collector/verify/{collector.verification_token}/"
found = []
if sent_dir.exists():
    for f in sorted(sent_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True):
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if token_str in text:
            found.append(str(f))

if found:
    print('Verification email already exists in:')
    for p in found:
        print(' - ' + p)
    exit(0)

# Not found -> resend
site_url = getattr(settings, 'SITE_URL', None) or 'http://127.0.0.1:8000'
verification_link = f"{site_url.rstrip('/')}/collector/verify/{collector.verification_token}/"
subject = 'Trashmandu - Verify your collector account'
message = f"Hi {user.first_name},\n\nClick this link to verify your collector account:\n{verification_link}\n\nThis link will expire in 24 hours.\n\nBest regards,\nTrashmandu Team"
from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@trashmandu.com')

print('Resending verification email to:', user.email)
try:
    send_mail(subject, message, from_email, [user.email], fail_silently=False)
    print('send_mail() completed — email attempt made.')
except Exception as e:
    print('Error sending email:', str(e))
    print('If using SMTP, ensure credentials and network are configured.')

# After attempting to send, check file backend directory for the new email (if applicable)
if sent_dir.exists():
    latest = sorted(sent_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True)
    if latest:
        print('Most recent file in sent_emails:')
        print(' -', latest[0])
else:
    print('sent_emails directory does not exist; if using SMTP backend, check SMTP logs or Gmail inbox.')
