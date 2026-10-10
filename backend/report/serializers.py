from rest_framework import serializers
from .models import PostReport, CommentReport

class PostReportSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post.title', read_only=True)
    post_content = serializers.CharField(source='post.content', read_only=True)
    reported_user = serializers.CharField(source='post.user.nickname', read_only=True)

    class Meta:
        model = PostReport
        fields = [
            'id', 'reporter', 'post', 'reason', 'created_at',
            'post_title', 'post_content', 'reported_user'
        ]



class CommentReportSerializer(serializers.ModelSerializer):
    comment_content = serializers.CharField(source='comment.content', read_only=True)
    post_title = serializers.CharField(source='comment.post.title', read_only=True)
    reported_user = serializers.CharField(source='comment.user.nickname', read_only=True)

    class Meta:
        model = CommentReport
        fields = [
            'id', 'reporter', 'comment', 'reason', 'created_at',
            'post_title', 'comment_content', 'reported_user'
        ]
        read_only_fields = ['reporter', 'created_at', 'comment_content', 'post_title', 'reported_user']