import os
import sys
import django

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trashmandu.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

c = Client()
username = 'regtest'
password = 'regpass123'
email = 'regtest@example.com'

# ensure user doesn't exist
User.objects.filter(username=username).delete()

resp = c.post('/collector/register/', {'username': username, 'email': email, 'password': password}, follow=True, HTTP_HOST='127.0.0.1')
print('Status code:', resp.status_code)
print('Redirect chain:', resp.redirect_chain)
print('Response length:', len(resp.content))
print('Templates:', [t.name for t in resp.templates])
print('--- body ---')
print(resp.content.decode(errors='replace')[:2000])

# Try posting again with same username to ensure unique check
resp2 = c.post('/collector/register/', {'username': username, 'email': email, 'password': password}, follow=True, HTTP_HOST='127.0.0.1')
print('\nSecond attempt:')
print('Status code:', resp2.status_code)
print('Redirect chain:', resp2.redirect_chain)
print('Response length:', len(resp2.content))
print('Templates:', [t.name for t in resp2.templates])
print('--- body ---')
print(resp2.content.decode(errors='replace')[:1000])
