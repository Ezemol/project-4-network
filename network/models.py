from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user")
    poster = models.ForeignKey("User", on_delete=models.PROTECT, related_name="poster")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id":self.id,
            "poster":self.poster,
            "body":self.body,
            "timestamp":self.timestamp,
            "likes":self.likes,
        }

    def like(self):
        self.likes += 1
        self.save()

    def dislike(self):
        self.likes -= 1
        self.save()