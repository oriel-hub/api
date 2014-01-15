from django.contrib.auth.models import User
from django.db.models import signals

from .models import UserProfile


def create_profile(sender, instance, signal, created, **kwargs):
    """When user is created also create a matching profile."""
    if created:
        if UserProfile.objects.filter(user=instance).count() == 0:
            UserProfile(user=instance).save()
            # Do additional stuff here if needed, e.g.
            # create other required related records

# When model instance is saved, trigger creation of corresponding profile
signals.post_save.connect(create_profile, sender=User)
