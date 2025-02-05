from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from products.models import Batch
from .models import ProductionRecord, LogisticsRecord, SalesRecord
from .serializers import ProductionRecordSerializer, LogisticsRecordSerializer, SalesRecordSerializer, TraceSerializer
from products.serializers import BatchSerializer
from .permissions import IsEnterpriseUser, IsSalesUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from django.db.models import Q

# Create your views here.

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductionRecordListCreateView(generics.ListCreateAPIView):
    """生产记录列表和创建"""
    serializer_class = ProductionRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = ProductionRecord.objects.all().order_by('-production_date')
        queryset = queryset.select_related('batch', 'batch__product', 'operator')
        
        batch = self.request.query_params.get('batch', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if batch:
            queryset = queryset.filter(batch_id=batch)
        if date_from:
            queryset = queryset.filter(production_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(production_date__lte=date_to)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print('Response data:', response.data)  # 添加调试日志
        return response

class ProductionRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """生产记录详情、更新和删除"""
    queryset = ProductionRecord.objects.all()
    serializer_class = ProductionRecordSerializer
    permission_classes = [IsAuthenticated]

class LogisticsRecordListCreateView(generics.ListCreateAPIView):
    """物流记录列表和创建"""
    serializer_class = LogisticsRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = LogisticsRecord.objects.all()
        batch = self.request.query_params.get('batch', None)
        status = self.request.query_params.get('status', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)

        if batch:
            queryset = queryset.filter(batch_id=batch)
        if status:
            queryset = queryset.filter(status=status)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.select_related('batch', 'operator')

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)

class LogisticsRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """物流记录详情、更新和删除"""
    queryset = LogisticsRecord.objects.all()
    serializer_class = LogisticsRecordSerializer
    permission_classes = [IsAuthenticated]

class SalesRecordListCreateView(generics.ListCreateAPIView):
    """销售记录列表和创建视图"""
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = SalesRecord.objects.select_related(
            'batch',
            'batch__product',
            'batch__product__category',
            'seller'
        ).order_by('-created_at')
        
        # 根据用户角色过滤数据
        if not self.request.user.is_staff:  # 非管理员
            queryset = queryset.filter(seller=self.request.user)
            
        # 过滤条件
        batch = self.request.query_params.get('batch', None)
        if batch:
            queryset = queryset.filter(batch__batch_number=batch)
            
        customer = self.request.query_params.get('customer', None)
        if customer:
            queryset = queryset.filter(customer_name__icontains=customer)
            
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class SalesRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """销售记录详情、更新和删除"""
    queryset = SalesRecord.objects.all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]

class TraceDetailView(APIView):
    """批次追溯详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_number):
        batch = get_object_or_404(Batch, batch_number=batch_number)
        
        # 获取完整的追溯链
        trace_data = {
            'batch': batch,
            'production': ProductionRecord.objects.filter(batch=batch).first(),
            'logistics': LogisticsRecord.objects.filter(batch=batch).order_by('created_at'),
            'sales': SalesRecord.objects.filter(batch=batch).order_by('sale_date')
        }
        
        serializer = TraceSerializer(trace_data)
        return Response(serializer.data)

class TraceScanView(APIView):
    """扫码追溯"""
    permission_classes = [IsAuthenticated]

    def get(self, request, qr_code):
        batch = get_object_or_404(Batch, qr_code=qr_code)
        
        # 获取完整的追溯链
        trace_data = {
            'batch': batch,
            'production': ProductionRecord.objects.filter(batch=batch).first(),
            'logistics': LogisticsRecord.objects.filter(batch=batch).order_by('created_at'),
            'sales': SalesRecord.objects.filter(batch=batch).order_by('sale_date')
        }
        
        serializer = TraceSerializer(trace_data)
        return Response(serializer.data)

class BatchTraceView(APIView):
    """批次追溯视图"""
    permission_classes = [AllowAny]
    
    def get(self, request, batch_number):
        batch = get_object_or_404(Batch, batch_number=batch_number)
        
        # 获取完整的追溯链
        trace_data = {
            'batch': BatchSerializer(batch).data,
            'production': ProductionRecordSerializer(
                batch.production_records.all(), many=True
            ).data,
            'logistics': LogisticsRecordSerializer(
                batch.logistics_records.all(), many=True
            ).data,
            'sales': SalesRecordSerializer(
                batch.sales_records.all(), many=True
            ).data
        }
        
        return Response(trace_data)

class QRCodeView(APIView):
    """二维码生成视图"""
    permission_classes = [AllowAny]
    
    def get(self, request, batch_number):
        try:
            batch = Batch.objects.get(batch_number=batch_number)
            # 生成二维码的逻辑
            # ...
            return Response({'qrcode_url': batch.qr_code.url})
        except Batch.DoesNotExist:
            return Response({'error': '批次不存在'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def search_batches(request):
    """搜索批次号"""
    query = request.query_params.get('query', '')
    batches = Batch.objects.filter(
        Q(batch_number__icontains=query) |
        Q(product__name__icontains=query)
    ).select_related('product')[:10]
    
    return Response([{
        'batch_number': batch.batch_number,
        'product_name': batch.product.name,
        'production_date': batch.production_date
    } for batch in batches])

@api_view(['GET'])
def recent_batches(request):
    """获取最近的批次"""
    batches = Batch.objects.select_related('product').order_by('-created_at')[:10]
    
    return Response([{
        'batch_number': batch.batch_number,
        'product_name': batch.product.name,
        'production_date': batch.production_date
    } for batch in batches])

@api_view(['GET'])
def trace_batch(request, batch_number):
    """获取批次追溯信息"""
    try:
        batch = Batch.objects.select_related(
            'product',
            'product__manufacturer'
        ).prefetch_related(
            'production_records__operator',
            'logistics_records__operator',
            'sales_records__seller'
        ).get(batch_number=batch_number)
        
        trace_data = {
            'batch_number': batch.batch_number,
            'product': {
                'name': batch.product.name,
                'specifications': batch.product.specifications,
                'code': batch.product.code,
                'manufacturer_name': batch.product.manufacturer.username  # 只返回用户名
            },
            'production_date': batch.production_date,
            'expiry_date': batch.expiry_date,
            'production_records': [{
                'production_date': record.production_date,
                'production_line': record.production_line,
                'operator_name': record.operator.username,  # 只返回用户名
                'temperature': str(record.temperature),
                'humidity': str(record.humidity),
                'quality_check': record.quality_check or []
            } for record in batch.production_records.all()],
            'logistics_records': [{
                'record_type': record.record_type,
                'from_location': record.from_location,
                'to_location': record.to_location,
                'operation_time': record.created_at,
                'status': record.status,
                'operator_name': record.operator.username  # 只返回用户名
            } for record in batch.logistics_records.all()],
            'sales_record': None
        }

        # 获取销售记录
        try:
            sales_record = batch.sales_records.latest('created_at')
            trace_data['sales_record'] = {
                'sale_date': sales_record.sale_date,
                'quantity': sales_record.quantity,
                'unit_price': str(sales_record.unit_price),
                'total_amount': str(sales_record.total_amount),
                'payment_method': sales_record.payment_method,
                'transaction_id': sales_record.transaction_id,
                'customer_name': sales_record.customer_name,
                'seller_name': sales_record.seller.username  # 只返回用户名
            }
        except SalesRecord.DoesNotExist:
            pass

        return Response(trace_data)
        
    except Batch.DoesNotExist:
        return Response({'error': '未找到该批次信息'}, status=404)
    except Exception as e:
        print(f"Error in trace_batch: {str(e)}")
        return Response({'error': str(e)}, status=500)
