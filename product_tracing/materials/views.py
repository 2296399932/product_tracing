from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
# 尝试导入django-filter，如果不存在则忽略
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None

from .models import Supplier, Material, MaterialBatch, MaterialSupplier
from .serializers import SupplierSerializer, MaterialSerializer, MaterialBatchSerializer, MaterialSupplierSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SupplierViewSet(viewsets.ModelViewSet):
    """供应商管理视图集"""
    queryset = Supplier.objects.all().order_by('id')
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    # 只有在django-filter可用时才设置过滤器
    if DjangoFilterBackend:
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields = ['name', 'contact_person']
        search_fields = ['name', 'contact_person', 'phone', 'address']
        ordering_fields = ['name', 'created_at']
        ordering = ['-created_at']
    else:
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        search_fields = ['name', 'contact_person', 'phone', 'address']
        ordering_fields = ['name', 'created_at']
        ordering = ['-created_at']

    # 可选：自定义分页响应格式
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'count': queryset.count()
        })

class MaterialViewSet(viewsets.ModelViewSet):
    """原材料管理视图集"""
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Material.objects.all()
    pagination_class = StandardResultsSetPagination
    
    # 添加过滤功能
    if DjangoFilterBackend:
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields = ['category', 'status', 'origin']
        search_fields = ['name', 'code', 'description']
        ordering_fields = ['name', 'created_at']
        ordering = ['-created_at']
    else:
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        search_fields = ['name', 'code', 'description']
        ordering_fields = ['name', 'created_at']
        ordering = ['-created_at']
    
    def get_queryset(self):
        """扩展查询集以支持更多过滤条件"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        name = self.request.query_params.get('name__icontains')
        
        # 应用过滤条件
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset
    
    @action(detail=True, methods=['get', 'post'])
    def suppliers(self, request, pk=None):
        """获取或添加材料的供应商关联"""
        material = self.get_object()
        
        if request.method == 'GET':
            material_suppliers = MaterialSupplier.objects.filter(material=material)
            serializer = MaterialSupplierSerializer(material_suppliers, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            supplier_id = request.data.get('supplier_id')
            is_preferred = request.data.get('is_preferred', False)
            
            try:
                supplier = Supplier.objects.get(id=supplier_id)
                
                if MaterialSupplier.objects.filter(material=material, supplier=supplier).exists():
                    return Response(
                        {'error': '该供应商已关联到此材料'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                material_supplier = MaterialSupplier.objects.create(
                    material=material,
                    supplier=supplier,
                    is_preferred=is_preferred
                )
                
                serializer = MaterialSupplierSerializer(material_supplier)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
            except Supplier.DoesNotExist:
                return Response(
                    {'error': '供应商不存在'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['get', 'put', 'delete'], url_path='suppliers/(?P<supplier_id>[^/.]+)')
    def supplier_detail(self, request, pk=None, supplier_id=None):
        """获取、更新或删除特定的材料-供应商关联"""
        material = self.get_object()
        
        try:
            material_supplier = MaterialSupplier.objects.get(
                material=material,
                id=supplier_id
            )
            
            if request.method == 'GET':
                serializer = MaterialSupplierSerializer(material_supplier)
                return Response(serializer.data)
                
            elif request.method == 'PUT':
                # 只更新首选状态
                is_preferred = request.data.get('is_preferred', material_supplier.is_preferred)
                material_supplier.is_preferred = is_preferred
                material_supplier.save()
                
                serializer = MaterialSupplierSerializer(material_supplier)
                return Response(serializer.data)
                
            elif request.method == 'DELETE':
                material_supplier.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
                
        except MaterialSupplier.DoesNotExist:
            return Response(
                {'error': '找不到指定的材料-供应商关联'},
                status=status.HTTP_404_NOT_FOUND
            )

class MaterialBatchViewSet(viewsets.ModelViewSet):
    """原材料批次管理视图集"""
    serializer_class = MaterialBatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MaterialBatch.objects.all()
    pagination_class = StandardResultsSetPagination

    # 添加过滤功能
    if DjangoFilterBackend:
        filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
        filterset_fields = ['material', 'material_id', 'supplier', 'supplier_id', 'status']
        search_fields = ['batch_number']
        ordering_fields = ['production_date', 'expiry_date', 'created_at', 'price']
        ordering = ['-created_at']
    else:
        filter_backends = [filters.SearchFilter, filters.OrderingFilter]
        search_fields = ['batch_number']
        ordering_fields = ['production_date', 'expiry_date', 'created_at', 'price']
        ordering = ['-created_at']
    
    def get_queryset(self):
        """扩展查询集以支持更多过滤条件"""
        queryset = super().get_queryset()
        
        # 获取查询参数
        material_id = self.request.query_params.get('material_id')
        batch_number = self.request.query_params.get('batch_number__icontains')
        
        # 应用过滤条件
        if material_id:
            queryset = queryset.filter(material_id=material_id)
        
        if batch_number:
            queryset = queryset.filter(batch_number__icontains=batch_number)
            
        return queryset

    def perform_create(self, serializer):
        """创建批次时设置创建者"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def use_material(self, request, pk=None):
        """使用原材料，更新状态"""
        batch = self.get_object()
        if batch.status != 'in_storage':
            return Response({'error': '只有在库状态的原材料才能被使用'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        batch.status = 'used'
        batch.save()
        return Response({'status': 'success'}) 