from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Category, Product, Batch
from .permissions import IsManufacturerOrAdmin
from .serializers import CategorySerializer, ProductSerializer, BatchSerializer
from tracing.permissions import IsEnterpriseUser
from rest_framework.pagination import PageNumberPagination
import qrcode
import base64
from io import BytesIO
from django.conf import settings
import os
from rest_framework.decorators import api_view


# Create your views here.

class CategoryListCreateView(generics.ListCreateAPIView):
    """商品分类列表和创建"""
    queryset = Category.objects.filter(is_active=True)  # 只返回激活的分类
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # 禁用分页，返回所有分类

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """商品分类详情、更新和删除"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListCreateView(generics.ListCreateAPIView):
    """商品列表和创建"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination

    def get_queryset(self):
        queryset = Product.objects.all()
        category = self.request.query_params.get('category', None)
        name = self.request.query_params.get('name', None)
        
        if category:
            queryset = queryset.filter(category_id=category)
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """商品详情、更新和删除"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class BatchListCreateView(generics.ListCreateAPIView):
    """批次列表和创建"""
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination  # 使用相同的分页类

    def get_queryset(self):
        queryset = Batch.objects.all().order_by('-created_at')  # 按创建时间倒序
        
        # 获取查询参数
        batch_number = self.request.query_params.get('batch_number')
        product = self.request.query_params.get('product')
        production_date_from = self.request.query_params.get('production_date_from')
        production_date_to = self.request.query_params.get('production_date_to')
        
        # 应用过滤条件
        if batch_number:
            queryset = queryset.filter(batch_number__icontains=batch_number)
        if product:
            queryset = queryset.filter(product_id=product)
        if production_date_from:
            queryset = queryset.filter(production_date__gte=production_date_from)
        if production_date_to:
            queryset = queryset.filter(production_date__lte=production_date_to)
            
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """批次详情、更新和删除"""
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
def generate_qrcode(request, batch_number):
    """生成批次二维码"""
    try:
        # 创建二维码数据
        qr_data = f"{settings.FRONTEND_URL}/trace/{batch_number}"
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # 创建图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_image = base64.b64encode(buffer.getvalue()).decode()
        
        return Response({
            'qrcode_url': f"data:image/png;base64,{qr_image}",
            'batch_number': batch_number,
            'trace_url': qr_data
        })
        
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return Response({'error': '生成二维码失败'}, status=500)
