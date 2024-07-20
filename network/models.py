from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=280)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post made by: {self.user} at time {self.date}"
    
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="currentUser")
    followingUser = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="followingUser")

    def __str__(self):
        return f"User {self.user} is following {self.followingUser}"


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE ,related_name="userLike")
    post = models.ForeignKey(Post, on_delete=models.CASCADE ,related_name="postLike")

    def __str__(self):
        return f"{self.user} liked {self.post}"

    