from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Post(models.Model):
    """Database model for tracking events"""

    author = models.ForeignKey("Neighbor", on_delete=models.CASCADE, related_name="posts")
    type = models.ForeignKey("PostType", on_delete=models.CASCADE, related_name="posts" )
    title = models.CharField(max_length=200)
    publication_date = models.DateField(auto_now_add=True)
    event_date = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())], blank=True, null=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    content = models.CharField(max_length=200)
    approved = models.BooleanField()
    categories = models.ManyToManyField("Category", through="PostCategory", related_name="posts")
    accept_rsvp = models.BooleanField(default=False)