from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Warning
from products.models import Product, Category, Batch
from tracing.models import SalesRecord

User = get_user_model()

class DashboardTests(APITestCase):
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # 登录
        self.client.force_authenticate(user=self.user)
        
        # 创建测试数据
        self.category = Category.objects.create(name='测试分类')
        self.product = Product.objects.create(
            name='测试商品',
            category=self.category,
            price=100.00
        )
        self.batch = Batch.objects.create(
            product=self.product,
            batch_number='TEST001',
            production_date='2024-01-01',
            expiry_date='2025-01-01',
            quantity=100
        )
        self.warning = Warning.objects.create(
            title='测试预警',
            content='测试内容',
            level='high'
        )

    def test_overview_endpoint(self):
        url = reverse('dashboard:overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('productCount', response.data)
        self.assertIn('warningCount', response.data)

    def test_sales_trend_endpoint(self):
        url = reverse('dashboard:sales_trend')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('dates', response.data)
        self.assertIn('amounts', response.data)

    def test_category_stats_endpoint(self):
        url = reverse('dashboard:category_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 只有一个测试分类

    def test_latest_orders_endpoint(self):
        url = reverse('dashboard:latest_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_warnings_endpoint(self):
        # 测试获取预警列表
        url = reverse('dashboard:warnings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # 测试创建新预警
        data = {
            'title': '新预警',
            'content': '新预警内容',
            'level': 'medium'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_OK)

        # 测试更新预警状态
        warning_url = reverse('dashboard:warning_detail', args=[self.warning.id])
        response = self.client.put(warning_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Warning.objects.get(id=self.warning.id).is_resolved)
