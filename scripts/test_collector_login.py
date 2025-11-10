import os
import sys
import django

# Ensure project root is on sys.path so Django settings package can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from collectorapp.models import CollectorProfile

username = 'testcollector'
password = 'testpass123'

user, created = User.objects.get_or_create(username=username, defaults={'email': 'test@example.com'})
if created:
    user.set_password(password)
    user.save()
    print('Created user', username)
else:
    print('User already exists')

# Ensure no collector profile initially
CollectorProfile.objects.filter(user=user).delete()
print('Deleted any existing CollectorProfile for user')

c = Client()
resp = c.post('/collector/login/', {'username': username, 'password': password}, follow=True, HTTP_HOST='127.0.0.1')
print('LOGIN ATTEMPT WITHOUT PROFILE')
print('Status code:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)
print('Template names:', [t.name for t in resp.templates])
print('Response length:', len(resp.content))
print('--- response body (first 1000 chars) ---')
print(resp.content.decode(errors='replace')[:1000])

# Now create a collector profile and try again
profile, pcreated = CollectorProfile.objects.get_or_create(user=user, defaults={'email_verified': True})
print('CollectorProfile created:', pcreated)

resp2 = c.post('/collector/login/', {'username': username, 'password': password}, follow=True, HTTP_HOST='127.0.0.1')
print('\nLOGIN ATTEMPT WITH PROFILE')
print('Status code:', resp2.status_code)
print('Redirect chain:', resp2.redirect_chain)
print('Template names:', [t.name for t in resp2.templates])
print('Response length:', len(resp2.content))
print('--- response body (first 1000 chars) ---')
print(resp2.content.decode(errors='replace')[:1000])
