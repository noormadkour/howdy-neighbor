from django.db import models


class PostType(models.Model):

    type = models.CharField(max_length=200)
    