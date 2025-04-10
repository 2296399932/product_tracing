from rest_framework import serializers
from .models import ProductionRecord, LogisticsRecord, SalesRecord
from products.serializers import BatchSerializer

class ProductionRecordSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    batch_details = BatchSerializer(source='batch', read_only=True)
    
    class Meta:
        model = ProductionRecord
        fields = [
            'id', 'batch', 'batch_number', 'batch_details',
            'production_date', 'production_line',
            'operator', 'operator_name',
            'temperature', 'humidity',
            'quality_check', 'remark', 'created_at'
        ]
        read_only_fields = ['operator', 'created_at']

class LogisticsRecordSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    batch_details = serializers.SerializerMethodField()
    
    class Meta:
        model = LogisticsRecord
        fields = [
            'id',
            'batch',
            'batch_details',
            'batch_number',
            'record_type',
            'from_location',
            'to_location',
            'operator',
            'operator_name',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'operator', 'updated_at']
    
    def get_batch_details(self, obj):
        return {
            'product_name': obj.batch.product.name,
            'specifications': obj.batch.product.specifications,
            'manufacturer_name': obj.batch.product.manufacturer.username
        }

class SalesRecordSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    batch_number = serializers.CharField(source='batch.batch_number', read_only=True)
    batch_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SalesRecord
        fields = [
            'id', 'batch', 'batch_number', 'batch_details',
            'customer_name', 'customer_phone', 'customer_address',
            'quantity', 'unit_price', 'total_amount',
            'payment_method', 'transaction_id', 'sale_date',
            'seller', 'seller_name', 'remark', 'created_at'
        ]
        read_only_fields = ['seller', 'total_amount']
    
    def validate(self, data):
        # 验证并计算总金额
        quantity = data.get('quantity', 0)
        unit_price = data.get('unit_price', 0)
        total_amount = quantity * unit_price
        
        if total_amount <= 0:
            raise serializers.ValidationError({'total_amount': '总金额必须大于0'})
        
        data['total_amount'] = total_amount
        return data
    
    def get_batch_details(self, obj):
        try:
            if not obj.batch:
                return None
                
            return {
                'id': obj.batch.id,
                'batch_number': obj.batch.batch_number,
                'quantity': obj.batch.quantity,
                'product': {
                    'id': obj.batch.product.id,
                    'name': obj.batch.product.name,
                    'category_name': obj.batch.product.category.name,
                    'specifications': obj.batch.product.specifications
                }
            }
        except Exception as e:
            print(f"Error getting batch details: {e}")
            return None

class TraceSerializer(serializers.Serializer):
    batch = serializers.CharField(source='batch_number')
    product = serializers.SerializerMethodField()
    production_records = serializers.SerializerMethodField()
    logistics_records = serializers.SerializerMethodField()
    sales_record = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    def get_product(self, obj):
        return {
            'name': obj.product.name,
            'specifications': obj.product.specifications,
            'code': obj.product.code,
            'manufacturer_name': obj.product.manufacturer.username
        }

    def get_materials(self, obj):
        try:
            # 添加调试日志
            print(f"Getting materials for batch {obj.batch_number}")
            print(f"Product: {obj.product.name}")
            print(f"Product materials count: {obj.product.product_materials.count()}")
            
            materials = []
            for pm in obj.product.product_materials.all():
                try:
                    material_batch = pm.material_batch
                    print(f"Processing material batch: {material_batch.batch_number}")
                    
                    materials.append({
                        'name': material_batch.material.name,
                        'code': material_batch.material.code,
                        'batch_number': material_batch.batch_number,
                        'quantity': str(pm.quantity),
                        'unit': pm.unit,
                        'supplier': material_batch.supplier.name if material_batch.supplier else None,
                        'production_date': material_batch.production_date,
                        'expiry_date': material_batch.expiry_date
                    })
                except Exception as e:
                    print(f"Error processing material: {str(e)}")
                    continue
                
            return materials
        except Exception as e:
            print(f"Error in get_materials: {str(e)}")
            return []

    def get_production_records(self, obj):
        return [{
            'production_date': record.production_date,
            'production_line': record.production_line,
            'operator_name': record.operator.username,
            'temperature': str(record.temperature),
            'humidity': str(record.humidity),
            'quality_check': record.quality_check or []
        } for record in obj.production_records.all()]

    def get_logistics_records(self, obj):
        return [{
            'record_type': record.record_type,
            'from_location': record.from_location,
            'to_location': record.to_location,
            'operation_time': record.created_at,
            'status': record.status,
            'operator_name': record.operator.username
        } for record in obj.logistics_records.all()]

    def get_sales_record(self, obj):
        try:
            record = obj.sales_records.latest('created_at')
            return {
                'sale_date': record.sale_date,
                'quantity': record.quantity,
                'unit_price': str(record.unit_price),
                'total_amount': str(record.total_amount),
                'payment_method': record.payment_method,
                'transaction_id': record.transaction_id,
                'customer_name': record.customer_name,
                'seller_name': record.seller.username
            }
        except SalesRecord.DoesNotExist:
            return None 