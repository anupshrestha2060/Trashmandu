from django.db import models
from django.contrib.auth.models import User
import uuid

# ---------------------------
# USER PROFILE
# ---------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True)
    is_verified = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username


# ---------------------------
# PLASTIC TYPE
# ---------------------------
class PlasticType(models.Model):
    name = models.CharField(max_length=50)
    price_per_kg = models.FloatField(default=12)

    def __str__(self):
        return self.name


# ---------------------------
# PICKUP REQUEST
# ---------------------------
class PickupRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    assigned_collector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_pickups')

    def __str__(self):
        return f"{self.user.username} - {self.scheduled_date}"
    
    def get_total_weight(self):
        """Calculate total weight of plastic items in this pickup"""
        return sum(item.weight for item in self.plasticitem_set.all())
    
    def get_total_amount(self):
        """Calculate total amount for this pickup"""
        return sum(item.weight * item.price_at_time for item in self.plasticitem_set.all())


# ---------------------------
# PLASTIC ITEM
# ---------------------------
class PlasticItem(models.Model):
    pickup_request = models.ForeignKey(PickupRequest, on_delete=models.CASCADE)
    plastic_type = models.ForeignKey(PlasticType, on_delete=models.SET_NULL, null=True)
    weight = models.FloatField()
    price_at_time = models.FloatField()

    def __str__(self):
        return f"{self.plastic_type.name} - {self.weight}kg"
