#!/usr/bin/env python
"""
Scan sent_emails for verification/reset links and map tokens to profiles.
Prints a list of matches for user to review.
"""
import os
import django
from pathlib import Path
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE','trashmandu.settings')
django.setup()

from userapp.models import UserProfile
from collectorapp.models import CollectorProfile

BASE = Path(__file__).resolve().parent
sent_dir = Path(getattr(__import__('django.conf').conf.settings,'EMAIL_FILE_PATH', BASE / 'sent_emails'))

pattern = re.compile(r"/(user|collector)/(verify|reset-password)/([A-Za-z0-9\-_/]+)")

results = []
if not sent_dir.exists():
    print('No sent_emails directory found at', sent_dir)
    exit(0)

files = sorted(sent_dir.iterdir(), key=lambda p: p.stat().st_ctime, reverse=True)
for f in files:
    try:
        txt = f.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    for m in pattern.finditer(txt):
        kind = m.group(1)  # user|collector
        action = m.group(2)  # verify|reset-password
        token = m.group(3).strip('/')
        entry = {'file': str(f.name), 'kind': kind, 'action': action, 'token': token}
        # lookup profile
        if kind == 'user' and action == 'verify':
            try:
                p = UserProfile.objects.get(verification_token=token)
                entry['profile'] = f'user:{p.user.username} <{p.user.email}>'
                entry['status'] = 'verified' if p.is_verified else 'unverified'
            except UserProfile.DoesNotExist:
                entry['profile'] = 'no-match'
                entry['status'] = 'n/a'
        elif kind == 'user' and action == 'reset-password':
            try:
                p = UserProfile.objects.get(password_reset_token=token)
                entry['profile'] = f'user:{p.user.username} <{p.user.email}>'
                entry['status'] = 'reset-token-set'
            except UserProfile.DoesNotExist:
                entry['profile'] = 'no-match'
                entry['status'] = 'n/a'
        elif kind == 'collector' and action == 'verify':
            try:
                p = CollectorProfile.objects.get(verification_token=token)
                entry['profile'] = f'collector:{p.user.username} <{p.user.email}>'
                entry['status'] = 'verified' if p.is_verified else 'unverified'
            except CollectorProfile.DoesNotExist:
                entry['profile'] = 'no-match'
                entry['status'] = 'n/a'
        elif kind == 'collector' and action == 'reset-password':
            try:
                p = CollectorProfile.objects.get(password_reset_token=token)
                entry['profile'] = f'collector:{p.user.username} <{p.user.email}>'
                entry['status'] = 'reset-token-set'
            except CollectorProfile.DoesNotExist:
                entry['profile'] = 'no-match'
                entry['status'] = 'n/a'
        results.append(entry)

# Print results
if not results:
    print('No verification/reset links found in sent_emails files.')
else:
    print('Found the following links in sent_emails:')
    for i, r in enumerate(results, 1):
        print(f"{i}. file={r['file']} kind={r['kind']} action={r['action']} token={r['token']}")
        print(f"   profile={r['profile']} status={r['status']}")

print('\nTo simulate delivery/verification, please reply with the numbers to act on (e.g. `1` or `1,3`).')
print('Or reply `all` to simulate all listed actions.')
