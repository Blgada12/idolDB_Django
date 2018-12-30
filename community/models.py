from django.db import models
from django.utils import timezone

from users.models import User


class CameLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    info = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
