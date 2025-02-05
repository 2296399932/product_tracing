from rest_framework import serializers
from .models import Warning
from products.models import Product, Category, Batch, Inventory
from tracing.models import SalesRecord

class WarningSerializer(serializers.ModelSerializer):
    """预警信息序列化器"""
    class Meta:
        model = Warning
        fields = ['id', 'title', 'content', 'level', 'is_resolved', 'created_at']
        read_only_fields = ['created_at']

class DashboardOverviewSerializer(serializers.Serializer):
    """仪表盘概览数据序列化器"""
    productCount = serializers.IntegerField()
    productGrowth = serializers.FloatField()
    batchCount = serializers.IntegerField()
    inventoryValue = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthSales = serializers.DecimalField(max_digits=12, decimal_places=2)
    salesGrowth = serializers.FloatField()
    warningCount = serializers.IntegerField()
    expiringCount = serializers.IntegerField()

class OrderSerializer(serializers.ModelSerializer):
    """订单信息序列化器"""
    customer = serializers.CharField(source='customer.username')
    product_name = serializers.CharField(source='batch.product.name')
    
    class Meta:
        model = SalesRecord
        fields = ['id', 'order_number', 'customer', 'product_name', 
                 'amount', 'status', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""
    product_count = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['name', 'product_count', 'total_sales']

class SalesDataSerializer(serializers.Serializer):
    """销售数据序列化器"""
    date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    count = serializers.IntegerField() 