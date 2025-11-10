from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date

class CollectorProfile(models.Model):
    date_of_birth = models.DateField(null=False, default='2000-01-01')  # default date
    phone_number = models.CharField(max_length=20, null=False, default='N/A')  # default phone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    citizenship_id = models.CharField(max_length=20, default='NA')
    def is_adult(self):
        return (date.today().year - self.date_of_birth.year) >= 18

    def __str__(self):
        return f"{self.user.username}'s Collector Profile"
