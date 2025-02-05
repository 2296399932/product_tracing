from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from products.models import Product, Batch
from tracing.models import SalesRecord

def get_date_range(days=30):
    """获取日期范围"""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date

def calculate_growth_rate(current, previous):
    """计算增长率"""
    if not previous:
        return 0
    return ((current - previous) / previous) * 100

def get_sales_trend(start_date, end_date, granularity='day'):
    """获取销售趋势数据"""
    sales = SalesRecord.objects.filter(
        created_at__range=(start_date, end_date)
    )
    
    if granularity == 'day':
        sales = sales.extra({
            'date': "DATE(created_at)"
        })
    elif granularity == 'week':
        sales = sales.extra({
            'date': "DATE(DATE_SUB(created_at, INTERVAL WEEKDAY(created_at) DAY))"
        })
    else:  # month
        sales = sales.extra({
            'date': "DATE_FORMAT(created_at, '%Y-%m-01')"
        })
    
    sales = sales.values('date').annotate(
        amount=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')
    
    return sales

def get_expiring_batches(days=30):
    """获取即将过期的批次"""
    warning_date = timezone.now().date() + timedelta(days=days)
    return Batch.objects.filter(
        expiry_date__lte=warning_date,
        status='in_storage'
    ) 