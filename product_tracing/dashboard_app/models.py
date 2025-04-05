from django.db import models

class Warning(models.Model):
    """系统预警模型"""
    LEVEL_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )

    TYPE_CHOICES = (
        ('stock', '库存不足'),
        ('expiry', '即将过期'),
        ('quality', '质量问题'),
        ('system', '系统异常'),
    )
    
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES, default='system')
    level = models.CharField('级别', max_length=10, choices=LEVEL_CHOICES)
    target = models.CharField('预警对象', max_length=100, blank=True)
    is_resolved = models.BooleanField('是否已解决', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '系统预警'
        verbose_name_plural = verbose_name
        db_table = 'dashboard_warning'

    def __str__(self):
        return f"{self.get_type_display()}-{self.title}"

    def save(self, *args, **kwargs):
        # 如果是新创建的预警，根据类型自动设置级别
        if not self.pk:
            if self.type == 'expiry':
                self.level = 'high'
            elif self.type == 'stock':
                self.level = 'medium'
            elif self.type == 'quality':
                self.level = 'high'
            else:
                self.level = 'low'
        super().save(*args, **kwargs)


class DashboardSetting(models.Model):
    """仪表盘设置"""
    setting_key = models.CharField('键', max_length=50, unique=True)
    value = models.JSONField('值')
    description = models.CharField('描述', max_length=200, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '仪表盘设置'
        verbose_name_plural = verbose_name
        db_table = 'dashboard_setting'

    def __str__(self):
        return self.setting_key


class Notification(models.Model):
    """通知消息"""
    TYPE_CHOICES = (
        ('warning', '预警'),
        ('system', '系统'),
        ('task', '任务'),
    )
    
    title = models.CharField('标题', max_length=100)
    content = models.TextField('内容')
    type = models.CharField('类型', max_length=20, choices=TYPE_CHOICES)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, 
                            related_name='notifications', verbose_name='用户')
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '通知消息'
        verbose_name_plural = verbose_name
        db_table = 'dashboard_notification'

    def __str__(self):
        return f"{self.user.username}-{self.title}" 