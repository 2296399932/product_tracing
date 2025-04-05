from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import Category, Product, Batch, ProductMaterial

from .serializers import CategorySerializer, ProductSerializer, BatchSerializer, BatchMaterialSerializer

from rest_framework.pagination import PageNumberPagination
import qrcode
import base64
from io import BytesIO
from django.conf import settings
import os
from rest_framework.decorators import api_view, action
from rest_framework.parsers import MultiPartParser, FormParser
import uuid


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
    
    def get_serializer_context(self):
        """
        添加请求到序列化器上下文，以便生成完整的图片URL
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """商品详情、更新和删除"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        """
        添加请求到序列化器上下文，以便生成完整的图片URL
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """
        重写retrieve方法，添加错误处理
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            print(f"Error retrieving product: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"获取商品详情失败: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        重写update方法，添加错误处理
        """
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            print(f"Error updating product: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"更新商品失败: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class BatchListCreateView(generics.ListCreateAPIView):
    """批次列表和创建"""
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination

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

    def get_serializer_context(self):
        """
        添加请求到序列化器上下文，以便生成完整的图片URL
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """批次详情、更新和删除"""
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def update(self, request, *args, **kwargs):
        """重写update方法，添加详细错误处理"""
        import traceback
        try:
            # 打印接收到的数据
            print(f"收到的批次更新数据: {request.data}")
            
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            # 打印当前对象状态
            print(f"当前批次数据: ID={instance.id}, 批次号={instance.batch_number}")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            # 输出验证错误
            if not serializer.is_valid():
                print(f"序列化器验证错误: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            print(f"批次更新错误: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": f"更新批次失败: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


# @api_view(['GET'])
# def generate_qrcode(request, batch_number):
#     try:
#         # 创建二维码数据
#         qr_data = f"{settings.FRONTEND_URL}/trace/{batch_number}"
#
#         # 生成二维码
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(qr_data)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
#
#         # 确保目录存在
#         qr_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
#         os.makedirs(qr_dir, exist_ok=True)
#
#         # 保存图片
#         file_path = os.path.join(qr_dir, f"{batch_number}.png")
#         img.save(file_path)
#
#         # 返回URL
#         qr_url = f"{settings.MEDIA_URL}qrcodes/{batch_number}.png"
#
#         print(f"二维码已保存: {file_path}")
#         print(f"二维码URL: {qr_url}")
#
#         return Response({
#             'qrcode_url': qr_url,
#             'batch_number': batch_number,
#             'trace_url': qr_data
#         })
#
#     except Exception as e:
#         print(f"Error generating QR code: {str(e)}")
#         return Response({'error': '生成二维码失败'}, status=500)
# 修改图片上传视图
class ProductImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('file')
        if not image_file:
            return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查文件类型
        if not image_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return Response({'error': '只支持PNG、JPG格式的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 生成唯一文件名
        ext = os.path.splitext(image_file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        file_path = os.path.join(settings.MEDIA_ROOT, 'products', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # 返回图片URL
        image_url = f"{request.build_absolute_uri(settings.MEDIA_URL)}products/{filename}"
        return Response({'image_url': image_url}, status=status.HTTP_201_CREATED)

# 添加一个新的视图类来处理批次原材料
class BatchMaterialsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """获取批次关联的原材料"""
        try:
            batch = Batch.objects.get(pk=pk)
            materials = ProductMaterial.objects.filter(product=batch.product)
            materials_data = []
            for material in materials:
                materials_data.append({
                    'id': material.id,
                    'material_batch': material.material_batch.id,
                    'material_name': material.material_batch.material.name,
                    'batch_number': material.material_batch.batch_number,
                    'quantity': material.quantity,
                    'unit': material.unit
                })
            return Response(materials_data)
        except Batch.DoesNotExist:
            return Response({"error": "批次不存在"}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, pk):
        """为批次添加原材料"""
        try:
            batch = Batch.objects.get(pk=pk)
            
            # 处理批量添加原材料的情况
            if 'materials' in request.data and isinstance(request.data['materials'], list):
                materials_data = request.data['materials']
                created_materials = []
                
                # 先删除产品的现有材料关联，采用替换而非追加的方式
                ProductMaterial.objects.filter(product=batch.product).delete()
                
                for material_data in materials_data:
                    # 为每个原材料创建关联
                    material_serializer = BatchMaterialSerializer(data=material_data)
                    if material_serializer.is_valid():
                        material = material_serializer.save(product=batch.product)
                        created_materials.append({
                            'id': material.id,
                            'material_batch': material.material_batch.id,
                            'material_name': material.material_batch.material.name,
                            'batch_number': material.material_batch.batch_number,
                            'quantity': material.quantity,
                            'unit': material.unit
                        })
                    else:
                        return Response(material_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                return Response(created_materials, status=status.HTTP_201_CREATED)
            else:
                # 处理单个原材料添加
                # 先检查是否已存在
                material_batch_id = request.data.get('material_batch')
                existing = ProductMaterial.objects.filter(
                    product=batch.product, 
                    material_batch_id=material_batch_id
                ).first()
                
                if existing:
                    # 已存在，更新现有记录
                    serializer = BatchMaterialSerializer(existing, data=request.data, partial=True)
                    if serializer.is_valid():
                        material = serializer.save()
                        return Response({
                            'id': material.id,
                            'material_batch': material.material_batch.id,
                            'material_name': material.material_batch.material.name,
                            'batch_number': material.material_batch.batch_number,
                            'quantity': material.quantity,
                            'unit': material.unit
                        }, status=status.HTTP_200_OK)
                else:
                    # 不存在，创建新记录
                    serializer = BatchMaterialSerializer(data=request.data)
                    if serializer.is_valid():
                        material = serializer.save(product=batch.product)
                        return Response({
                            'id': material.id,
                            'material_batch': material.material_batch.id,
                            'material_name': material.material_batch.material.name,
                            'batch_number': material.material_batch.batch_number,
                            'quantity': material.quantity,
                            'unit': material.unit
                        }, status=status.HTTP_201_CREATED)
                
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Batch.DoesNotExist:
            return Response({"error": "批次不存在"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
