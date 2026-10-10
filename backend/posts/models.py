from django.db import models
from django.conf import settings
from accounts.models import User



class Board(models.Model):
    name = models.CharField(max_length=100, unique=True)
    board_name = models.CharField(max_length=100)
        
    def __str__(self):
        return self.board_name

class Post(models.Model):
    title = models.CharField(max_length = 100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now_add= True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    views = models.PositiveIntegerField(default = 0)
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_posts', blank = True)
    dislike = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name= 'dislike_posts', blank = True)
    board = models.ForeignKey(Board, on_delete = models.CASCADE)
    
    def __str__(self):
        return self.title
    
class Comment(models.Model): 
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add = True, null = False, blank = False)
    content = models.TextField(default='')
    parent = models.ForeignKey('self', null = True, blank=True, on_delete = models.CASCADE, related_name='replies')
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.content
    
    #  parent 대신 클래스 하나 더 만들기. self 별로임

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('post', '게시글'),
        ('comment', '댓글'),
    )
    
    reporter = models.ForeignKey(User, on_delete = models.CASCADE)
    report_type = models.CharField(max_length=10, choices = REPORT_TYPE_CHOICES)
    object_id = models.PositiveIntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add= True)
    
    def __str__(self):
        return f"{self.report_type} #{self.object_id} 신고 by {self.reporter.username}"

   
class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE, related_name='media') # 어떤 게시글에 첨부된 파일인지 연결, 게시글 하나당 N개 파일, post.media로 첨부파일에 접근 가능
    file = models.FileField(upload_to='post_media/') # 실제 업로드되는 파일 필드. media/post_media/ 경로에 저장
    
    def __str__(self):
        return f"{self.post.title} - {self.file.name}" #admin이나 shell에서 좋게 볼 수 있게끔 출력