from django.db import models
from django.contrib.auth.models import User


class Neighbor(models.Model):
    """Database model for tracking events"""

    address = models.CharField(max_length=200)
    bio = models.CharField(max_length=200)
    profile_image = models.URLField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="neighbors")