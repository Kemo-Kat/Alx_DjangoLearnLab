from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    def __str__(self):
        return self.username
    
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True)
    
    def __str__(self):
        return self.username
    
    def follow(self, user):
        """Add a user to followers"""
        if user != self:
            self.followers.add(user)
    
    def unfollow(self, user):
        """Remove a user from followers"""
        self.followers.remove(user)
    
    def is_following(self, user):
        """Check if following a user"""
        return self.followers.filter(id=user.id).exists()