from rest_framework import serializers
from .models import Supplier, Material, MaterialBatch, MaterialSupplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class MaterialSerializer(serializers.ModelSerializer):
    suppliers = serializers.SerializerMethodField()
    
    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_suppliers(self, obj):
        suppliers_link = MaterialSupplier.objects.filter(material=obj)
        return MaterialSupplierSerializer(suppliers_link, many=True).data

class MaterialBatchSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source='material.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = MaterialBatch
        fields = [
            'id', 'material', 'material_name', 'supplier', 'supplier_name',
            'batch_number', 'quantity', 'unit', 'production_date', 'expiry_date',
            'price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 如果没有提供 price，尝试从 MaterialSupplier 获取
        if 'price' not in validated_data:
            material = validated_data.get('material')
            supplier = validated_data.get('supplier')
            if material and supplier:
                try:
                    material_supplier = MaterialSupplier.objects.get(
                        material=material,
                        supplier=supplier
                    )
                    validated_data['price'] = material_supplier.price
                except MaterialSupplier.DoesNotExist:
                    validated_data['price'] = 0
        
        return super().create(validated_data)

class MaterialSupplierSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    material_name = serializers.CharField(source='material.name', read_only=True)
    
    class Meta:
        model = MaterialSupplier
        fields = ['id', 'material', 'material_name', 'supplier', 'supplier_name', 'is_preferred', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 