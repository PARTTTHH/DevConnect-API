from django.db import models
from accounts.models import User


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('FOLLOW', 'New Follower'),
        ('CONNECTION_REQUEST', 'Connection Request'),
        ('CONNECTION_ACCEPTED', 'Connection Accepted'),
        ('PROJECT_STAR', 'Project Starred'),
        ('PROJECT_COMMENT', 'Project Comment'),
        ('POST_LIKE', 'Post Liked'),
        ('POST_COMMENT', 'Post Comment'),
        ('OTHER', 'General Notification'),
    )

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caused_notifications')
    verb = models.CharField(max_length=255)
    target_url = models.CharField(max_length=255, blank=True, default='')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, default='OTHER', db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.username}: {self.actor.username} {self.verb}'
