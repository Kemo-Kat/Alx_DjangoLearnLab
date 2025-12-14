from django.db import models
from django.conf import settings

# Create your models here.

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='actor_notifications')
    verb = models.CharField(max_length=100)  # e.g., "liked your post", "commented on", "followed you"
    target_post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, null=True, blank=True)
    target_comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):

        return f"{self.actor.username} {self.verb}"
ass Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='actor_notifications')
    verb = models.CharField(max_length=100)
    target_post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, null=True, blank=True)
    target_comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, null=True, blank=True)
    read = models.BooleanField(default=False)

    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.actor.username} {self.verb}"


