#!/usr/bin/env python
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE','trashmandu.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from collectorapp.models import CollectorProfile
from userapp.models import UserProfile

sent_dir = Path(getattr(settings,'EMAIL_FILE_PATH', Path(settings.BASE_DIR)/'sent_emails'))
print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('EMAIL_FILE_PATH:', sent_dir)

# Find most recent password reset tokens for collector and user
print('\nLooking for CollectorProfile with password_reset_token...')
collectors = CollectorProfile.objects.exclude(password_reset_token__isnull=True).exclude(password_reset_token__exact='').order_by('-id')[:5]
if not collectors:
    print('  No CollectorProfile with non-empty password_reset_token found.')
else:
    for c in collectors:
        print(f"  Collector: {c.user.username} <{c.user.email}> token={c.password_reset_token}")

print('\nLooking for UserProfile with password_reset_token...')
users = UserProfile.objects.exclude(password_reset_token__isnull=True).exclude(password_reset_token__exact='').order_by('-id')[:5]
if not users:
    print('  No UserProfile with non-empty password_reset_token found.')
else:
    for u in users:
        print(f"  User: {u.user.username} <{u.user.email}> token={u.password_reset_token}")

# Ask for target email from env var
target = os.environ.get('CHECK_EMAIL')
if not target:
    print('\nNo target email specified (set CHECK_EMAIL env var to narrow search). Will search all recent files for any reset links.')

# Search sent_emails for reset links
if sent_dir.exists():
    files = sorted(sent_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True)[:50]
    matches = []
    for f in files:
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        if 'reset-password' in txt or 'Reset your password' in txt or 'Reset your password' in txt:
            if target:
                if target in txt or ('reset-password' in txt and target in txt):
                    matches.append((f, txt))
            else:
                matches.append((f, txt))
    if matches:
        print('\nFound reset-like email files:')
        for p, txt in matches:
            print(' -', p)
            # show snippet around reset link
            idx = txt.find('reset-password')
            start = max(0, idx-80)
            print('   snippet:', txt[start:start+200].replace('\n',' '))
    else:
        print('\nNo reset emails found in the latest sent_emails files.')
else:
    print('\nSent email directory does not exist:', sent_dir)

print('\nDone.')
