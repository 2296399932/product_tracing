from rest_framework import serializers
from .models import Category, Product, Batch
from users.serializers import UserSerializer
from django.db import models
from django.utils import timezone

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    manufacturer = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'category', 'category_name',
            'specifications', 'manufacturer', 'price', 'unit',
            'description', 'image', 'status', 'created_at', 'updated_at',
            'stock'
        ]
        read_only_fields = ['created_at', 'updated_at', 'manufacturer', 'stock']
    
    def get_stock(self, obj):
        """计算商品的可用库存（所有正常状态批次的数量之和）"""
        try:
            # 只统计状态为正常且未过期的批次库存
            return obj.batches.filter(
                status='active',  # 正常状态
                expiry_date__gt=timezone.now().date()  # 未过期
            ).aggregate(
                total_stock=models.Sum('quantity')
            )['total_stock'] or 0
        except Exception as e:
            print(f"Error calculating stock: {e}")
            return 0
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # 从 request 中获取当前用户作为制造商
            instance = Product.objects.create(
                manufacturer=request.user,
                **validated_data
            )
            return instance
        return super().create(validated_data)

class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = Batch
        fields = [
            'id', 'batch_number', 'product', 'product_name',
            'production_date', 'expiry_date', 'quantity',
            'cost_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # 验证生产日期和过期日期
        if data.get('expiry_date') and data.get('production_date'):
            if data['expiry_date'] <= data['production_date']:
                raise serializers.ValidationError({
                    'expiry_date': '过期日期必须大于生产日期'
                })
        
        # 验证数量和成本价为正数
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError({
                'quantity': '数量必须大于0'
            })
        if data.get('cost_price', 0) <= 0:
            raise serializers.ValidationError({
                'cost_price': '成本价必须大于0'
            })
            
        return data