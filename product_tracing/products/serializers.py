from rest_framework import serializers
from .models import Category, Product, Batch, Inventory, InventoryRecord, ProductMaterial
from users.serializers import UserSerializer
from django.db import models
from django.utils import timezone
from django.conf import settings
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    manufacturer = UserSerializer(read_only=True)
    category_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'code', 'category', 'category_name',
            'specifications', 'manufacturer', 'price', 'unit',
            'description', 'image', 'image_url', 'status', 'created_at', 'updated_at',
            'stock'
        ]
        read_only_fields = ['created_at', 'updated_at', 'manufacturer', 'stock', 'image_url']
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
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
    
    def update(self, instance, validated_data):
        """
        重写update方法，确保正确处理图片字段和规格字段
        """
        # 如果前端传入了image字段但值为空字符串，则不更新该字段
        if 'image' in validated_data and validated_data['image'] == '':
            validated_data.pop('image')
        
        # 处理specifications字段，确保它是一个字典
        if 'specifications' in validated_data:
            specs = validated_data['specifications']
            if isinstance(specs, str):
                try:
                    # 尝试解析JSON字符串
                    validated_data['specifications'] = json.loads(specs)
                except json.JSONDecodeError:
                    # 如果解析失败，将其作为普通字符串处理
                    validated_data['specifications'] = {'description': specs}
            elif not specs:
                validated_data['specifications'] = {}
        
        return super().update(instance, validated_data)

class BatchMaterialSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material_batch.material.name', read_only=True)
    batch_number = serializers.CharField(source='material_batch.batch_number', read_only=True)
    
    class Meta:
        model = ProductMaterial
        fields = ['id', 'material_batch', 'material_name', 'batch_number', 'quantity', 'unit']
        extra_kwargs = {
            'material_batch': {'required': True},
            'quantity': {'required': True}
        }

class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField()
    product_details = ProductSerializer(source='product', read_only=True)
    materials = serializers.SerializerMethodField()
    
    class Meta:
        model = Batch
        fields = [
            'id', 'batch_number', 'product', 'product_name',
            'production_date', 'expiry_date', 'quantity',
            'cost_price', 'status', 'created_at', 'updated_at',
            'product_image', 'product_details', 'materials'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_product_image(self, obj):
        if obj.product and obj.product.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.product.image.url)
            return obj.product.image.url
        return None

    def get_materials(self, obj):
        """获取批次关联的原材料信息"""
        materials = ProductMaterial.objects.filter(product=obj.product)
        return BatchMaterialSerializer(materials, many=True).data

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

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'