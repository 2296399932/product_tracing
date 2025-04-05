import os

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
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
import qrcode
import io
from django.core.files.base import ContentFile
from django.conf import settings
import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

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
    permission_classes = [AllowAny]  # 已改为允许任何人访问
    pagination_class = StandardResultsSetPagination  # 添加分页配置
    
    def get_queryset(self):
        print("\n=== SalesRecord 查询开始 ===")
        print(f"当前用户: {self.request.user.username}, 角色: {getattr(self.request.user, 'role', 'unknown')}")
        print(f"请求参数: {self.request.query_params}")
        
        queryset = SalesRecord.objects.select_related(
            'batch',
            'batch__product',
            'batch__product__category',
            'seller'
        ).order_by('-created_at')
        
        print(f"初始查询集记录数: {queryset.count()}")
        
        # 注释掉这部分代码，让所有用户都能看到所有销售记录
        # if not self.request.user.is_staff:  # 非管理员
        #     queryset = queryset.filter(seller=self.request.user)
        #     print(f"过滤后记录数(只显示当前用户): {queryset.count()}")
            
        # 过滤条件
        batch = self.request.query_params.get('batch', None)
        if batch:
            queryset = queryset.filter(batch__batch_number=batch)
            print(f"批次过滤后记录数: {queryset.count()}, 批次: {batch}")
            
        customer = self.request.query_params.get('customer', None)
        if customer:
            queryset = queryset.filter(customer_name__icontains=customer)
            print(f"客户名称过滤后记录数: {queryset.count()}, 客户名称: {customer}")
            
        # 打印最终结果
        result_count = queryset.count()
        print(f"最终查询结果记录数: {result_count}")
        if result_count > 0:
            print("查询结果样例:")
            for record in queryset[:3]:  # 只显示前3条
                print(f"- ID: {record.id}, 批次: {record.batch.batch_number}, 客户: {record.customer_name}")
        else:
            print("查询结果为空!")
            
            # 检查是否存在任何销售记录
            total_records = SalesRecord.objects.count()
            print(f"数据库中销售记录总数: {total_records}")
            if total_records > 0:
                print("数据库中存在销售记录样例:")
                for record in SalesRecord.objects.all()[:3]:
                    print(f"- ID: {record.id}, 批次: {record.batch.batch_number}, 客户: {record.customer_name}, 销售员: {record.seller.username}")
        
        print("=== SalesRecord 查询结束 ===\n")
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

class SalesRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """销售记录详情、更新和删除"""
    queryset = SalesRecord.objects.all()
    serializer_class = SalesRecordSerializer
    permission_classes = [IsAuthenticated]

class TraceView(APIView):
    """追溯查询视图"""
    permission_classes = [AllowAny]
    
    def get(self, request, batch_number):
        try:
            logger.info(f"Trace request for batch: {batch_number} from {request.META.get('REMOTE_ADDR')}")
            logger.info(f"User agent: {request.META.get('HTTP_USER_AGENT')}")
            
            batch = Batch.objects.select_related(
                'product',
                'product__manufacturer',
            ).prefetch_related(
                'production_records',
                'production_records__operator',
                'logistics_records',
                'logistics_records__operator',
                'sales_records',
                'sales_records__seller',
                'product__product_materials',
                'product__product_materials__material_batch',
                'product__product_materials__material_batch__material',
                'product__product_materials__material_batch__supplier'
            ).get(batch_number=batch_number)
            
            logger.info(f"Batch found: {batch.batch_number}, product: {batch.product.name}")
            
            serializer = TraceSerializer(batch)
            response_data = serializer.data
            
            # 记录响应大小
            logger.info(f"Response data size: {len(str(response_data))} characters")
            
            return Response(response_data)
        except Batch.DoesNotExist:
            logger.warning(f"Batch not found: {batch_number}")
            return Response({'error': '批次不存在'}, status=404)
        except Exception as e:
            logger.error(f"Error in trace view: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=500)

class TraceScanView(APIView):
    """扫码追溯"""
    permission_classes = [AllowAny]

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
            # 创建二维码数据
            qr_data = f"{settings.FRONTEND_URL}/#/trace/{batch_number}"

            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")

            # 确保目录存在
            qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
            os.makedirs(qr_dir, exist_ok=True)

            # 保存图片
            file_path = os.path.join(qr_dir, f"{batch_number}.png")
            img.save(file_path)

            # 返回URL
            qr_url = f"http://192.168.1.108:8000{settings.MEDIA_URL}qrcodes/{batch_number}.png"

            print(f"二维码已保存: {file_path}")
            print(f"二维码URL: {qr_url}")

            return Response({
                'qrcode_url': qr_url,
                'batch_number': batch_number,
                'trace_url': qr_data
            })

        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return Response({'error': '生成二维码失败'}, status=500)

class PublicTraceView(APIView):
    """公开的追溯 API，供前端调用"""
    permission_classes = [AllowAny]
    
    def get(self, request, qr_code):
        try:
            batch = Batch.objects.get(qr_code=qr_code)
            # 获取追溯数据
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
        except Batch.DoesNotExist:
            return Response({'error': '未找到该批次信息'}, status=404)

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

def public_trace_page(request, batch_number):
    """公开访问的追溯页面"""
    batch = get_object_or_404(Batch, batch_number=batch_number)
    # 获取所有追溯数据
    context = {
        'batch': batch,
        'production': batch.production_records.first(),
        'logistics': batch.logistics_records.all(),
        'sales': batch.sales_records.all()
    }
    return render(request, 'tracing/public_trace.html', context)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    简单的健康检查API，测试手机是否可以连接到后端
    """
    return Response({
        'status': 'ok',
        'message': '服务正常运行',
        'client_ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT')
    })

def test_connection(request):
    """超简单的连接测试页面"""
    return HttpResponse("""
    <html>
        <head><title>连接测试</title></head>
        <body>
            <h1>连接成功!</h1>
            <p>您的IP: {}</p>
            <p>用户代理: {}</p>
        </body>
    </html>
    """.format(
        request.META.get('REMOTE_ADDR', '未知'),
        request.META.get('HTTP_USER_AGENT', '未知')
    ))
