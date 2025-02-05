from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Batch
from data_analysis.models import TracingStatistics
from tracing.models import ProductionRecord
import random
from datetime import timedelta

class Command(BaseCommand):
    help = '生成测试数据'

    def handle(self, *args, **options):
        # 获取所有批次
        batches = Batch.objects.all()
        
        for batch in batches:
            # 生成追溯查询记录
            for _ in range(random.randint(1, 10)):
                TracingStatistics.objects.create(
                    batch=batch,
                    date=timezone.now().date() - timedelta(days=random.randint(0, 30)),
                    scan_count=random.randint(1, 100),
                    query_count=random.randint(1, 50),
                    region=random.choice(['北京', '上海', '广州', '深圳'])
                )
            
            # 生成生产记录和质检数据
            quality_results = ['pass', 'failed']
            issue_types = ['包装破损', '标签错误', '重量不足']
            severities = ['轻微', '一般', '严重']
            statuses = ['pending', 'processing', 'resolved']
            
            ProductionRecord.objects.create(
                batch=batch,
                production_date=timezone.now() - timedelta(days=random.randint(0, 30)),
                quality_check=[{
                    'item': '质量检查',
                    'result': random.choice(quality_results),
                    'standard': '产品标准',
                    'process_time': random.randint(10, 120),
                    'issue_type': random.choice(issue_types),
                    'severity': random.choice(severities),
                    'status': random.choice(statuses),
                    'description': '质量问题描述'
                }]
            ) 