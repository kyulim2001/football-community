from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.nickname')

    class Meta:
        model = Notification
        fields = ['id', 'type', 'sender', 'post', 'comment', 'is_read', 'created_at']

