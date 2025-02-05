from django.db import models
from products.models import Batch, Product
from users.models import User

class ProductionRecord(models.Model):
    """生产记录"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, 
                             related_name='production_records', verbose_name='商品批次')
    raw_materials = models.JSONField(verbose_name='原材料信息')
    production_date = models.DateTimeField(
        verbose_name='生产时间',
        db_index=True  # 添加索引
    )
    operator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作员')
    quality_check = models.JSONField(verbose_name='质检信息')
    production_line = models.CharField(max_length=50, verbose_name='生产线')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, 
                                    null=True, blank=True, verbose_name='生产温度')
    humidity = models.DecimalField(max_digits=5, decimal_places=2, 
                                 null=True, blank=True, verbose_name='生产环境湿度')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '生产记录'
        verbose_name_plural = verbose_name
        db_table = 'production_record'

class LogisticsRecord(models.Model):
    """物流记录模型"""
    RECORD_TYPE_CHOICES = (
        ('storage', '入库'),
        ('delivery', '出库'),
        ('transport', '运输中')
    )
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成')
    )
    
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, 
                             related_name='logistics_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    from_location = models.CharField(max_length=100)
    to_location = models.CharField(max_length=100)
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '物流记录'
        verbose_name_plural = verbose_name
        db_table = 'logistics_record'

class SalesRecord(models.Model):
    """销售记录"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, 
                             related_name='sales_records', verbose_name='商品批次')
    customer_name = models.CharField(max_length=100, verbose_name='客户名称')
    customer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='客户电话')
    customer_address = models.CharField(max_length=200, blank=True, null=True, verbose_name='客户地址')
    quantity = models.IntegerField(verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总金额')
    payment_method = models.CharField(max_length=50, verbose_name='支付方式')
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='交易编号')
    sale_date = models.DateTimeField(verbose_name='销售时间')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, 
                              related_name='sales', verbose_name='销售员')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '销售记录'
        verbose_name_plural = verbose_name
        db_table = 'sales_record'
