from django.db import models


class RSVP(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="rsvps")
    neighbor = models.ForeignKey("Neighbor", on_delete=models.CASCADE, related_name="rsvps")  # Assuming Neighbor is a custom user model
    attending = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['post', 'neighbor'], name='unique_rsvp')
        ]