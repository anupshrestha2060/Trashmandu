from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date
import uuid


class CollectorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    citizenship_id = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username