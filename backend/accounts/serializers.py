from rest_framework import serializers
from .models import User, Block
from django.contrib.auth.password_validation import validate_password




class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data['email'],
            nickname = validated_data['nickname'],
            name = validated_data['username'],
            password = validated_data['password']
        )
        return user
    class Meta:
        model = User
        fields = ['nickname', 'email', 'username', 'password', 'is_active', 'id']
        
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'email', 'username']
        read_only_fields = fields

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'nickname', 'email']
        
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        old_password = self.validated_data['old_password']
        new_password = self.validated_data['new_password1']
        if not user.check_password(old_password):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        user.set_password(new_password)
        user.save()
    
    
class UserDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(write_only = True, required= True)
    
class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'blocked', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'nickname']
        read_only_fields = fields

        
        
    