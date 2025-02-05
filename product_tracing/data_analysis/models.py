from django.db import models
from products.models import Product, Batch
from users.models import User

class SalesStatistics(models.Model):
    """销售统计"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='sales_statistics', verbose_name='商品')
    date = models.DateField(verbose_name='统计日期')
    sales_count = models.IntegerField(default=0, verbose_name='销售数量')
    sales_amount = models.DecimalField(max_digits=12, decimal_places=2, 
                                     default=0, verbose_name='销售金额')
    customer_count = models.IntegerField(default=0, verbose_name='购买人数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '销售统计'
        verbose_name_plural = verbose_name
        db_table = 'sales_statistics'
        unique_together = ['product', 'date']

class TracingStatistics(models.Model):
    """追溯统计"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, 
                             related_name='tracing_statistics', verbose_name='商品批次')
    date = models.DateField(verbose_name='统计日期')
    scan_count = models.IntegerField(default=0, verbose_name='扫码次数')
    query_count = models.IntegerField(default=0, verbose_name='查询次数')
    region = models.CharField(max_length=100, verbose_name='查询地区')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '追溯统计'
        verbose_name_plural = verbose_name
        db_table = 'tracing_statistics'
        unique_together = ['batch', 'date', 'region']

class QualityAnalysis(models.Model):
    """质量分析"""
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, 
                             related_name='quality_analysis', verbose_name='商品批次')
    inspection_date = models.DateField(verbose_name='检测日期')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='检测员')
    quality_indicators = models.JSONField(verbose_name='质量指标')
    analysis_result = models.TextField(verbose_name='分析结果')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '质量分析'
        verbose_name_plural = verbose_name
        db_table = 'quality_analysis'
