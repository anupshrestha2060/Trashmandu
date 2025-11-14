from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=100, blank=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"


class PlasticType(models.Model):
    name = models.CharField(max_length=100)
    price_per_kg = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    recyclable = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - Rs.{self.price_per_kg}/kg"


class PickupRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_collector = models.ForeignKey(
        'collectorapp.CollectorProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def calculate_total_amount(self):
        return sum(item.subtotal for item in self.plasticitem_set.all())

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class PlasticItem(models.Model):
    pickup_request = models.ForeignKey(PickupRequest, on_delete=models.CASCADE)
    plastic_type = models.ForeignKey(PlasticType, on_delete=models.PROTECT)
    weight = models.FloatField()
    price_at_time = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def subtotal(self):
        return self.weight * self.price_at_time

    def save(self, *args, **kwargs):
        if not self.price_at_time:
            self.price_at_time = self.plastic_type.price_per_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plastic_type.name} - {self.weight}kg"
