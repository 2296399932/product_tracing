from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncDate
from datetime import timedelta
from .serializers import (
    DashboardOverviewSerializer, 
    WarningSerializer,
    OrderSerializer
)
from .models import Warning
from products.models import Product, Category, Batch
from tracing.models import SalesRecord
from rest_framework.decorators import api_view

# Create your views here.

class DashboardOverviewView(APIView):
    """仪表盘概览视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            now = timezone.now()
            last_month = now - timedelta(days=30)
            
            # 获取商品总数
            product_count = Product.objects.filter(status='active').count()
            
            # 获取在库批次数和库存总值
            batch_count = Batch.objects.filter(status='in_storage').count()
            inventory_value = Batch.objects.filter(status='in_storage').aggregate(
                total=Sum(F('quantity') * F('cost_price'))
            )['total'] or 0
            
            # 获取本月销售额
            month_sales = SalesRecord.objects.filter(
                created_at__gte=last_month
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            
            # 获取预警信息
            warning_count = Warning.objects.filter(is_resolved=False).count()
            expiring_count = Batch.objects.filter(
                expiry_date__lte=now + timedelta(days=30),
                status='in_storage'
            ).count()
            
            return Response({
                'productCount': product_count,
                'batchCount': batch_count,
                'inventoryValue': float(inventory_value) if inventory_value else 0,
                'monthSales': float(month_sales) if month_sales else 0,
                'warningCount': warning_count,
                'expiringCount': expiring_count
            })
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardSalesView(APIView):
    """销售趋势视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        type = request.GET.get('type', 'month')
        now = timezone.now()
        
        if type == 'month':
            start_date = now - timedelta(days=30)
            trunc_date = 'date'
        elif type == 'week':
            start_date = now - timedelta(days=7)
            trunc_date = 'date'
        else:
            start_date = now - timedelta(days=365)
            trunc_date = 'month'

        sales_data = SalesRecord.objects.filter(
            created_at__gte=start_date
        ).values(
            'created_at__' + trunc_date
        ).annotate(
            amount=Sum('total_amount'),
            count=Count('id')
        ).order_by('created_at__' + trunc_date)

        return Response({
            'dates': [x['created_at__' + trunc_date].strftime('%Y-%m-%d') 
                     for x in sales_data],
            'amounts': [float(x['amount']) for x in sales_data],
            'orders': [x['count'] for x in sales_data]
        })

class DashboardCategoriesView(APIView):
    """分类统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            categories = Category.objects.annotate(
                product_count=Count('products'),
                total_sales=Sum(
                    'products__batches__sales_records__total_amount',
                    filter=Q(
                        products__batches__sales_records__created_at__gte=timezone.now() - timedelta(days=30)
                    )
                )
            )
            
            return Response([{
                'name': c.name,
                'product_count': c.product_count,
                'total_sales': float(c.total_sales) if c.total_sales else 0
            } for c in categories])
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardOrdersView(APIView):
    """最新订单视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = SalesRecord.objects.select_related(
                'batch__product'
            ).order_by('-created_at')[:10]
            
            return Response([{
                'id': order.id,
                'order_number': order.transaction_id,
                'customer': order.customer_name,
                'product_name': order.batch.product.name,
                'amount': order.total_amount,
                'created_at': order.created_at
            } for order in orders])
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardWarningsView(APIView):
    """系统预警视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            warnings = Warning.objects.filter(
                is_resolved=False
            ).order_by('-level', '-created_at')[:10]
            
            return Response([{
                'id': w.id,
                'title': w.title,
                'content': w.content,
                'level': w.level,
                'created_at': w.created_at
            } for w in warnings])
        except Exception as e:
            return Response({
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = WarningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        warning = Warning.objects.get(pk=pk)
        warning.is_resolved = True
        warning.save()
        return Response({
            'id': warning.id,
            'title': warning.title,
            'content': warning.content,
            'level': warning.level,
            'created_at': warning.created_at
        })

@api_view(['GET'])
def overview(request):
    """获取概览数据"""
    try:
        total_products = Product.objects.count()
        total_batches = Batch.objects.count()
        total_sales = SalesRecord.objects.count()
        total_revenue = SalesRecord.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # 计算预警信息
        # 库存不足的批次数量
        low_stock_count = Batch.objects.filter(quantity__lt=10).count()
        
        # 30天内过期的批次数量
        expiry_date = timezone.now().date() + timedelta(days=30)
        expiring_count = Batch.objects.filter(expiry_date__lte=expiry_date).count()
        
        return Response({
            'total_products': total_products,
            'total_batches': total_batches,
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'productGrowth': 0,  # 可以根据实际需求计算
            'salesGrowth': 0,    # 可以根据实际需求计算
            'warningCount': low_stock_count + expiring_count,  # 总预警数
            'expiringCount': expiring_count  # 即将过期的批次数
        })
    except Exception as e:
        print(f"Error in overview: {str(e)}")
        return Response({'error': '获取概览数据失败'}, status=500)

@api_view(['GET'])
def category_stats(request):
    """获取分类统计"""
    try:
        stats = Category.objects.annotate(
            product_count=Count('products'),
            value=Count('products', distinct=True)  # 添加 value 字段用于饼图
        ).values('name', 'product_count', 'value')
        
        # 转换为饼图所需的数据格式
        return Response([{
            'name': item['name'],
            'value': item['product_count'],
            'percentage': item['value']  # 用于显示百分比
        } for item in stats])
    except Exception as e:
        print(f"Error in category_stats: {str(e)}")
        return Response({'error': '获取分类统计失败'}, status=500)

@api_view(['GET'])
def sales_trend(request):
    """获取销售趋势"""
    try:
        type = request.GET.get('type', 'month')
        today = timezone.now().date()
        
        # 根据类型设置起始日期
        if type == 'week':
            start_date = today - timedelta(days=7)
        elif type == 'month':
            start_date = today - timedelta(days=30)
        elif type == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=30)  # 默认显示一个月
        
        # 获取销售数据
        sales = SalesRecord.objects.filter(
            sale_date__date__gte=start_date
        ).annotate(
            sale_day=TruncDate('sale_date')
        ).values('sale_day').annotate(
            total=Sum('total_amount'),
            order_count=Count('id')  # 添加订单数量统计
        ).order_by('sale_day')
        
        # 生成日期范围并填充数据
        date_dict = {
            item['sale_day'].strftime('%Y-%m-%d'): {
                'total': float(item['total']),
                'count': item['order_count']
            } for item in sales
        }
        
        dates = []
        values = []
        orders = []
        current = start_date
        
        while current <= today:
            date_str = current.strftime('%Y-%m-%d')
            dates.append(date_str)
            data = date_dict.get(date_str, {'total': 0, 'count': 0})
            values.append(data['total'])
            orders.append(data['count'])
            current += timedelta(days=1)
        
        return Response({
            'dates': dates,
            'values': values,
            'orders': orders  # 添加订单数量数据
        })
        
    except Exception as e:
        print(f"Error in sales_trend: {str(e)}")
        return Response({'error': '获取销售趋势失败'}, status=500)

@api_view(['GET'])
def latest_orders(request):
    """获取最新订单"""
    try:
        orders = SalesRecord.objects.select_related(
            'batch', 'batch__product'
        ).order_by('-sale_date')[:5]
        
        return Response([{
            'order_number': order.transaction_id,  # 使用交易ID作为订单号
            'customer': order.customer_name,
            'amount': float(order.total_amount),
            'status': '已完成',  # 或者根据实际状态判断
            'date': order.sale_date.strftime('%Y-%m-%d %H:%M:%S')
        } for order in orders])
    except Exception as e:
        print(f"Error in latest_orders: {str(e)}")
        return Response({'error': '获取最新订单失败'}, status=500)

@api_view(['GET'])
def warnings(request):
    """获取系统预警"""
    try:
        warnings = []
        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 检查库存低于10的批次
        low_stock_batches = Batch.objects.filter(
            quantity__lt=10
        ).select_related('product')[:5]
        
        for batch in low_stock_batches:
            warnings.append({
                'type': '库存不足',
                'content': f'产品 {batch.product.name} (批次号: {batch.batch_number}) 库存不足',
                'created_at': current_time
            })
        
        # 检查30天内过期的批次
        expiry_date = timezone.now().date() + timedelta(days=30)
        expiring_batches = Batch.objects.filter(
            expiry_date__lte=expiry_date
        ).select_related('product')[:5]
        
        for batch in expiring_batches:
            warnings.append({
                'type': '即将过期',
                'content': f'产品 {batch.product.name} (批次号: {batch.batch_number}) 即将过期',
                'created_at': current_time
            })
        
        return Response(warnings)
    except Exception as e:
        print(f"Error in warnings: {str(e)}")
        return Response({'error': '获取系统预警失败'}, status=500)
