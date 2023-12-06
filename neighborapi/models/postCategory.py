from django.db import models


class PostCategory(models.Model):
    """Database model for tracking events"""

    category = models.ForeignKey("Category", on_delete=models.CASCADE, related_name="post_categories")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="post_categories" )
    