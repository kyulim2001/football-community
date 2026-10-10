from django.db import models
from django.conf import settings
from posts.models import Post, Comment

class Notification(models.Model):
    NOTI_TYPE_CHOICES = [
        ('comment', '댓글'),
        ('reply', '대댓글'),
        ('like', '좋아요'),
    ]

    type = models.CharField(max_length=20, choices=NOTI_TYPE_CHOICES)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        