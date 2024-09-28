from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    is_active = models.BooleanField(default=True)
    is_liked = models.BooleanField(default=False)

    def serialize(self):
        return {
            "id":self.id,
            "poster":self.user,
            "body":self.body,
            "timestamp":self.timestamp,
            "likes":self.likes.count(),
            "is_liked":self.is_liked,
        }

    def like(self, user):
        if not self.likes.filter(id=user.id).exists():  # Solo añadir si no existe
            self.likes.add(user)

    def dislike(self, user):
        if self.likes.filter(id=user.id).exists():  # Solo eliminar si existe
            self.likes.remove(user)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    followers = models.ManyToManyField(User, related_name="following", blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def serialize(self):
        return {
            "user": self.user.username,
            "followers_count": self.followers.count(),
            "following_count": self.user.following.count(),
        }
