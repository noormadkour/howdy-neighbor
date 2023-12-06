from django.db import models


class Comment(models.Model):
    """Database model for tracking events"""

    neighbor = models.ForeignKey("Neighbor", on_delete=models.CASCADE, related_name="comments" )
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=200)
    created_on = models.DateField(auto_now_add=True)
    