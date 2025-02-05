from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name='手机号')
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )
    
    role = models.CharField('用户角色', max_length=20, choices=ROLE_CHOICES, default='user')
    company_name = models.CharField('公司名称', max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='地址')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    # 添加 related_name 来解决冲突
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        db_table = 'user'
        
    def __str__(self):
        return self.username
