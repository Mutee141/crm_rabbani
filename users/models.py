from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('HR', 'HR'),
        ('GM', 'GM'),
        ('MANAGER', 'MANAGER'),
        ('TEAM_LEAD', 'TEAM LEAD'),
        ('BDE', 'BDE'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True, null=True)
    
    # Optional: Self-referencing field to build the hierarchy
    reporting_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subordinates'
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# users/models.py

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # We use get_or_create to prevent the IntegrityError 
        # if the Admin Inline already created the profile
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Use a safer check to see if profile exists before saving
    if hasattr(instance, 'profile'):
        instance.profile.save()