from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.conf import settings
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import PermissionsMixin

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, nickname, username, password = None):
        if not email:
            raise ValueError("이메일이 필요합니다")
        if not nickname:
            raise ValueError("닉네임이 필요합니다")
        if not username:
            raise ValueError("이름이 필요합니다")
        user = self.model(
            email = self.normalize_email(email),
            nickname = nickname,
            username = username
        )
        user.set_password(password)
        user.save(using = self.db)
        return user
    
    def create_superuser(self, email, nickname, username, password = None):
        user = self.create_user(
            email = email,
            nickname = nickname,
            username = username,
            password = password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(default='', max_length=100, null=False, blank=False, unique=True)
    nickname = models.CharField(default='', max_length=100, null=False, blank=False, unique=True)
    username = models.CharField(default='', max_length=100, null=False, blank=False, unique=True)
    first_name = models.CharField(max_length = 30, blank = True)
    last_name = models.CharField(max_length = 30, blank = True)
    
    is_active = models.BooleanField(default=True)    
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nickname']

    def __str__(self):
        return self.nickname
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    nickname = models.CharField(max_length = 40, blank = True)
    introduction = models.TextField(blank = True)
    image = ProcessedImageField(
        blank = True,
        upload_to = 'profile/images',
        processors = [ResizeToFill(300, 300)],
        format = 'JPEG',
        options = {'quality': 90},
    )

class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete = models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.blocker.username}님이 {self.blocked.username}님을 차단했습니다."
    
class EmailVerification(models.Model):
    email = models.EmailField()
    code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    is_verified = models.BooleanField(default=False)
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    class Meta:
        get_latest_by = 'created_at'
    
            
