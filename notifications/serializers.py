from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserPublicSerializer


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserPublicSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'target_url', 'notification_type', 'is_read', 'created_at']
        read_only_fields = ['id', 'actor', 'verb', 'target_url', 'notification_type', 'created_at']
