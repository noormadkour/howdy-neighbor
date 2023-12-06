from django.db import models


class PostType(models.Model):
    """Database model for tracking events"""

    type = models.CharField(max_length=200)
    