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
        code = str(random.randint(100000, 999999))
        profile = UserProfile.objects.create(user=instance, verification_code=code)
        # Send verification email if the user has an email address
        if instance.email:
            subject = 'Verify your Trashmandu account'
            message = f"Hi {instance.get_full_name() or instance.username},\n\nYour verification code is: {code}\n\nEnter this code on the verification page to activate your account.\n\nIf you didn't request this, please ignore this email.\n\nThanks,\nTrashmandu Team"
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or 'no-reply@example.com'
            try:
                send_mail(subject, message, from_email, [instance.email], fail_silently=False)
            except Exception:
                # If email sending fails, we don't want to break user creation; just continue
                pass
