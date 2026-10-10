from django.contrib import admin
from .models import PostReport, CommentReport

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'reported_user', 'post', 'reason', 'created_at')
    list_filter = ('reason', 'created_at')
    search_fields = ('reporter__nickname', 'post__title')
    
    @admin.display(description="신고 대상")
    def reported_user(self, obj):
        return obj.post.user.nickname

@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'reporter',
        'reported_user',
        'post_display',
        'reason',
        'created_at',
    )

    @admin.display(description="게시글 제목")
    def post_display(self, obj):
        return obj.comment.post.title

    @admin.display(description="신고 대상")
    def reported_user(self, obj):
        return obj.comment.user.nickname
