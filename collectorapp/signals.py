from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import CollectorProfile
import random

@receiver(post_save, sender=User)
def create_collector_profile(sender, instance, created, **kwargs):
    if created:
        CollectorProfile.objects.create(user=instance, verification_code=str(random.randint(100000, 999999)))
