from rest_framework import serializers
from .models import User

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']

    def validate_username(self, value):
        """验证用户名是否已存在"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("该用户名已被注册")
        return value

    def validate(self, data):
        """验证两次密码是否一致"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "两次输入的密码不一致"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'company_name', 'phone', 
                 'address', 'is_active', 'created_at']
        read_only_fields = ['created_at'] 