from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CollectorProfile
import random
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def create_collector_profile(sender, instance, created, **kwargs):
    if created:
        # Create a CollectorProfile for the user. Verification is not used in this project.
        try:
            CollectorProfile.objects.create(user=instance)
        except Exception:
            # If creation fails for any reason, don't block user creation
            pass
