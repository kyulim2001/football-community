from django.contrib import admin
from .models import Post, Comment, Board, Report, PostMedia

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'board_name']
    search_fields = ['name', 'board_name']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'board', 'created_at', 'views']
    search_fields = ['title', 'content', 'user__nickname']
    list_filter = ['created_at', 'board']
    raw_id_fields = ['user']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'content', 'created_at', 'is_deleted']
    search_fields = ['content', 'user__nickname', 'post__title']
    list_filter = ['created_at', 'is_deleted']
    raw_id_fields = ['user', 'post']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'report_type', 'object_id', 'reporter', 'created_at']
    search_fields = ['reporter__nickname', 'object_id']
    list_filter = ['report_type', 'created_at']
    raw_id_fields = ['reporter']

@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'file']
    search_fields = ['post__title']
    raw_id_fields = ['post']
