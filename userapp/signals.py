from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import random
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a UserProfile for the user. Email verification is not used in this project.
        try:
            UserProfile.objects.create(user=instance)
        except Exception:
            # If profile creation fails, don't block user creation
            pass
