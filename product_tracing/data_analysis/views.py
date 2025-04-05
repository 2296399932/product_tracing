from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, FloatField
from django.db.models.functions import Cast, TruncDate, TruncWeek, TruncMonth
from datetime import datetime, timedelta, timezone
from .models import SalesStatistics, TracingStatistics, QualityAnalysis
from .serializers import (SalesStatisticsSerializer, TracingStatisticsSerializer,
                         QualityAnalysisSerializer)
from products.models import Product, Category, Batch
from tracing.models import SalesRecord, ProductionRecord, LogisticsRecord
from django.http import HttpResponse
import xlsxwriter
from io import BytesIO
from django.db import models
from django.db.models import Q
from django.db.models import F

class SalesStatisticsView(APIView):
    """销售统计视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取查询参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        group_by = request.query_params.get('group_by', '').split(',')
        
        # 基础查询
        queryset = SalesRecord.objects.all()
        
        # 时间范围过滤
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)
            
        # 分组统计
        stats = {
            'total_sales': queryset.aggregate(
                total_amount=Sum('total_amount'),
                total_quantity=Sum('quantity')
            )
        }
        
        # 按产品分组
        if 'product' in group_by:
            product_stats = queryset.values(
                'batch__product__name'
            ).annotate(
                sales_amount=Sum('total_amount'),
                sales_quantity=Sum('quantity')
            )
            stats['product_stats'] = product_stats
            
        # 按地区分组
        if 'region' in group_by:
            region_stats = queryset.values(
                'customer__address'
            ).annotate(
                sales_amount=Sum('total_amount'),
                sales_quantity=Sum('quantity')
            )
            stats['region_stats'] = region_stats
            
        return Response(stats)

class SalesTrendView(APIView):
    """销售趋势视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        granularity = request.query_params.get('granularity', 'day')
        
        # 选择时间截断函数
        trunc_func = {
            'day': TruncDate,
            'week': TruncWeek,
            'month': TruncMonth
        }.get(granularity, TruncDate)
        
        # 统计销售趋势
        trends = SalesRecord.objects.annotate(
            date=trunc_func('sale_date')
        ).values('date').annotate(
            sales_amount=Sum('total_amount'),
            sales_quantity=Sum('quantity')
        ).order_by('date')
        
        return Response(list(trends))

class SalesRankingView(APIView):
    """销售排行视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取前10名产品销售排行
        product_ranking = SalesRecord.objects.values(
            'batch__product__name'
        ).annotate(
            sales_amount=Sum('total_amount'),
            sales_quantity=Sum('quantity')
        ).order_by('-sales_amount')[:10]
        
        return Response(list(product_ranking))

class TracingStatisticsView(APIView):
    """追溯统计视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        stats = TracingStatistics.objects.values(
            'batch__product__name'
        ).annotate(
            scan_count=Sum('scan_count'),
            query_count=Sum('query_count')
        )
        return Response(list(stats))

class TracingRegionView(APIView):
    """追溯地区分布视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        region_stats = TracingStatistics.objects.values(
            'region'
        ).annotate(
            scan_count=Sum('scan_count'),
            query_count=Sum('query_count')
        )
        return Response(list(region_stats))

class QualityAnalysisListView(generics.ListCreateAPIView):
    """质量分析列表视图"""
    serializer_class = QualityAnalysisSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = QualityAnalysis.objects.all()
        batch = self.request.query_params.get('batch', None)
        if batch:
            queryset = queryset.filter(batch_id=batch)
        return queryset

class QualityAnalysisDetailView(generics.RetrieveUpdateAPIView):
    """质量分析详情视图"""
    queryset = QualityAnalysis.objects.all()
    serializer_class = QualityAnalysisSerializer
    permission_classes = [IsAuthenticated]

class QualityReportView(APIView):
    """质量分析报告视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # 获取查询参数
        batch = request.query_params.get('batch')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # 基础查询
        queryset = QualityAnalysis.objects.all()
        
        # 条件过滤
        if batch:
            queryset = queryset.filter(batch_id=batch)
        if start_date:
            queryset = queryset.filter(inspection_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(inspection_date__lte=end_date)
            
        # 生成报告
        report = {
            'summary': {
                'total_inspections': queryset.count(),
                'pass_rate': queryset.filter(
                    quality_indicators__contains={'result': 'pass'}
                ).count() / queryset.count() if queryset.count() > 0 else 0
            },
            'details': QualityAnalysisSerializer(queryset, many=True).data
        }
        
        return Response(report)

class SalesAnalysisView(APIView):
    """销售分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            analysis_type = request.query_params.get('type', 'amount')

            # 构建基础查询
            queryset = SalesRecord.objects.all()
            
            # 添加过滤条件
            if date_from:
                queryset = queryset.filter(sale_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(sale_date__lte=date_to)
            if category:
                queryset = queryset.filter(batch__product__category_id=category)

            # 按时间分组统计
            sales_data = queryset.values('sale_date').annotate(
                amount=Sum('total_amount'),
                count=Count('id')
            ).order_by('sale_date')

            # 计算总计
            totals = {
                'total_amount': queryset.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'total_count': queryset.count(),
            }

            # 如果有数据，计算平均值
            if totals['total_count'] > 0:
                totals['avg_amount'] = totals['total_amount'] / totals['total_count']
            else:
                totals['avg_amount'] = 0

            # 按产品分组统计
            product_stats = queryset.values(
                'batch__product__name'
            ).annotate(
                amount=Sum('total_amount'),
                count=Count('id')
            ).order_by('-amount')[:10]

            return Response({
                'trend': list(sales_data),
                'totals': totals,
                'top_products': list(product_stats)
            })
            
        except Exception as e:
            print(f"Error in SalesAnalysisView: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TracingAnalysisView(APIView):
    """追溯分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')

            # 构建基础查询
            batches = Batch.objects.all()
            
            # 添加过滤条件
            if date_from:
                batches = batches.filter(created_at__gte=date_from)
            if date_to:
                batches = batches.filter(created_at__lte=date_to)
            if category:
                batches = batches.filter(product__category_id=category)

            # 追溯链完整性分析
            chain_stats = {
                'total': batches.count(),
                'with_production': batches.filter(
                    production_records__isnull=False
                ).distinct().count(),
                'with_logistics': batches.filter(
                    logistics_records__isnull=False
                ).distinct().count(),
                'with_sales': batches.filter(
                    sales_records__isnull=False
                ).distinct().count(),
                'complete_chain': batches.filter(
                    production_records__isnull=False,
                    logistics_records__isnull=False,
                    sales_records__isnull=False
                ).distinct().count()
            }

            # 追溯查询热点分析
            hotspot_data = batches.annotate(
                scan_count=Count('tracing_statistics'),
                query_total=Sum('tracing_statistics__query_count')
            ).values(
                'product__name',
                'batch_number'
            ).annotate(
                count=models.F('query_total')
            ).filter(
                count__gt=0
            ).order_by('-count')[:10]

            return Response({
                'chain': chain_stats,
                'hotspot': list(hotspot_data)
            })
            
        except Exception as e:
            print(f"Error in TracingAnalysisView: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QualityAnalysisView(APIView):
    """质量分析视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))

            # 构建基础查询
            production_records = ProductionRecord.objects.all()
            
            # 添加过滤条件
            if date_from:
                production_records = production_records.filter(
                    production_date__gte=date_from
                )
            if date_to:
                production_records = production_records.filter(
                    production_date__lte=date_to
                )
            if category:
                production_records = production_records.filter(
                    batch__product__category_id=category
                )

            # 质量问题分布
            quality_distribution = production_records.filter(
                quality_check__isnull=False
            ).values(
                'quality_check__0__result'  # 假设 quality_check 是 JSONField
            ).annotate(
                count=Count('id')
            ).exclude(
                quality_check__0__result=''
            )

            # 问题处理时效
            timeliness_data = production_records.filter(
                quality_check__0__result='failed'
            ).values(
                'batch__product__name'
            ).annotate(
                avg_process_time=Avg('quality_check__0__process_time')
            )

            # 质量问题记录分页
            start = (page - 1) * page_size
            end = start + page_size
            issues = production_records.filter(
                quality_check__0__result='failed'
            ).select_related(
                'batch__product'
            )[start:end]

            return Response({
                'distribution': list(quality_distribution),
                'timeliness': list(timeliness_data),
                'issues': {
                    'count': issues.count(),
                    'results': [
                        {
                            'batch_number': record.batch.batch_number,
                            'product_name': record.batch.product.name,
                            'issue_type': record.quality_check.get('issue_type'),
                            'severity': record.quality_check.get('severity'),
                            'status': record.quality_check.get('status'),
                            'created_at': record.created_at,
                            'description': record.quality_check.get('description')
                        }
                        for record in issues
                    ]
                }
            })
            
        except Exception as e:
            print(f"Error in QualityAnalysisView: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AnalysisExportView(APIView):
    """数据分析导出视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # 创建一个内存中的Excel文件
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            
            # 添加销售分析
            self.add_sales_sheet(workbook, request)
            
            # 添加追溯分析
            self.add_tracing_sheet(workbook, request)
            
            workbook.close()
            
            # 设置响应头
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=analysis_report.xlsx'
            
            return response
            
        except Exception as e:
            print(f"Error in AnalysisExportView: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def add_sales_sheet(self, workbook, request):
        worksheet = workbook.add_worksheet('销售分析')
        
        # 设置表头样式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # 写入表头
        headers = ['日期', '销售额', '销售量', '平均单价']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # 获取销售数据
        sales_data = SalesRecord.objects.values(
            'sale_date'
        ).annotate(
            amount=Sum('total_amount'),
            count=Count('id'),
            avg_price=Cast(
                Sum('total_amount') / Cast(Count('id'), FloatField()),
                output_field=FloatField()
            )
        ).order_by('sale_date')
        
        # 写入数据
        for row, data in enumerate(sales_data, 1):
            worksheet.write(row, 0, data['sale_date'].strftime('%Y-%m-%d'))
            worksheet.write(row, 1, float(data['amount'] or 0))
            worksheet.write(row, 2, data['count'])
            worksheet.write(row, 3, float(data['avg_price'] or 0))
    
    def add_tracing_sheet(self, workbook, request):
        worksheet = workbook.add_worksheet('追溯分析')
        
        # 设置表头样式
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        # 写入表头
        headers = ['批次号', '商品名称', '扫码次数', '查询次数', '地区']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # 获取追溯数据
        tracing_data = TracingStatistics.objects.select_related(
            'batch', 'batch__product'
        ).values(
            'batch__batch_number',
            'batch__product__name',
            'region'
        ).annotate(
            scan_count=Sum('scan_count'),
            query_count=Sum('query_count')
        ).order_by('-query_count')
        
        # 写入数据
        for row, data in enumerate(tracing_data, 1):
            worksheet.write(row, 0, data['batch__batch_number'])
            worksheet.write(row, 1, data['batch__product__name'])
            worksheet.write(row, 2, data['scan_count'])
            worksheet.write(row, 3, data['query_count'])
            worksheet.write(row, 4, data['region'])

class SalesOverviewView(APIView):
    """销售概览数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            
            # 构建基础查询
            queryset = SalesRecord.objects.all()
            
            # 添加过滤条件
            if date_from:
                queryset = queryset.filter(sale_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(sale_date__lte=date_to)
            if category:
                queryset = queryset.filter(batch__product__category_id=category)

            # 获取销售趋势数据
            trend_data = queryset.annotate(
                date=TruncDate('sale_date')
            ).values('date').annotate(
                amount=Sum('total_amount'),
                count=Count('id')
            ).order_by('date')

            # 计算销售概览数据
            total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0

            overview = {
                'total_amount': float(total_amount),
                'order_count': queryset.count(),
                'product_count': queryset.values('batch__product').distinct().count(),
                'customer_count': queryset.values('customer_name').distinct().count(),
                'growth': 0,  # 默认增长率为0
                'trends': {
                    'dates': [item['date'].strftime('%Y-%m-%d') for item in trend_data],
                    'amount': [float(item['amount']) for item in trend_data],
                    'count': [item['count'] for item in trend_data]
                }
            }
            
            # 计算同比增长
            if date_from:
                try:
                    date_from = datetime.strptime(date_from, '%Y-%m-%d')
                    last_period = queryset.filter(
                        sale_date__lt=date_from,
                        sale_date__gte=date_from - timedelta(days=30)
                    )
                    last_amount = last_period.aggregate(total=Sum('total_amount'))['total'] or 0
                    if last_amount > 0:
                        overview['growth'] = ((total_amount - last_amount) / last_amount * 100)
                except (ValueError, TypeError):
                    pass  # 如果日期格式错误，保持默认增长率为0

            print("Overview data:", overview)  # 添加调试输出
            return Response(overview)
            
        except Exception as e:
            import traceback
            print("Error in SalesOverviewView:", str(e))
            print(traceback.format_exc())
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TracingOverviewView(APIView):
    """追溯概览数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            
            # 构建基础查询
            batches = Batch.objects.all()
            
            # 添加过滤条件
            if date_from:
                batches = batches.filter(created_at__gte=date_from)
            if date_to:
                batches = batches.filter(created_at__lte=date_to)
            if category:
                batches = batches.filter(product__category_id=category)

            # 计算追溯概览数据
            overview = {
                'total_batches': batches.count(),
                'complete_chain': batches.filter(
                    production_records__isnull=False,
                    logistics_records__isnull=False,
                    sales_records__isnull=False
                ).distinct().count(),
                'scan_count': batches.aggregate(
                    total=Sum('tracing_statistics__scan_count')
                )['total'] or 0,
                'query_count': batches.aggregate(
                    total=Sum('tracing_statistics__query_count')
                )['total'] or 0
            }
            
            # 计算完整率
            overview['completion_rate'] = (
                overview['complete_chain'] / overview['total_batches'] * 100
                if overview['total_batches'] > 0 else 0
            )

            # 添加商品销售排行数据
            top_products = SalesRecord.objects.values(
                'batch__product__name'
            ).annotate(
                total_amount=Sum('total_amount'),
                total_count=Count('id')
            ).order_by('-total_amount')[:5]  # 获取销售额前5的商品

            # 添加销售分类占比数据
            category_sales = SalesRecord.objects.values(
                'batch__product__category__name'
            ).annotate(
                total_amount=Sum('total_amount')
            ).order_by('-total_amount')

            # 更新返回数据
            overview.update({
                'top_products': [
                    {
                        'name': item['batch__product__name'],
                        'value': float(item['total_amount']),
                        'count': item['total_count']
                    } for item in top_products
                ],
                'category_sales': [
                    {
                        'name': item['batch__product__category__name'],
                        'value': float(item['total_amount'])
                    } for item in category_sales
                ]
            })

            return Response(overview)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QualityOverviewView(APIView):
    """质量概览数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            
            # 构建基础查询
            records = ProductionRecord.objects.all()
            
            # 添加过滤条件
            if date_from:
                records = records.filter(production_date__gte=date_from)
            if date_to:
                records = records.filter(production_date__lte=date_to)
            if category:
                records = records.filter(batch__product__category_id=category)

            # 计算质量概览数据
            total_records = records.count()
            passed_records = records.filter(
                quality_check__contains=[{'result': 'pass'}]
            ).count()
            
            overview = {
                'total_inspections': total_records,
                'passed_count': passed_records,
                'issue_count': total_records - passed_records,
                'pass_rate': (passed_records / total_records * 100) if total_records > 0 else 0,
                'avg_process_time': records.filter(
                    quality_check__0__result='failed'
                ).aggregate(
                    avg_time=Avg('quality_check__0__process_time')
                )['avg_time'] or 0
            }

            # 添加趋势数据
            trend_data = records.annotate(
                date=TruncDate('production_date')
            ).values('date').annotate(
                total=Count('id'),
                passed=Count('id', filter=Q(quality_check__contains=[{'result': 'pass'}]))
            ).order_by('date')

            # 添加问题类型分布
            issue_types = records.filter(
                quality_check__0__result='failed'
            ).values(
                'quality_check__0__issue_type'
            ).annotate(
                count=Count('id')
            ).order_by('-count')

            # 添加原因分析
            causes = records.filter(
                quality_check__0__result='failed'
            ).values(
                'quality_check__0__cause'
            ).annotate(
                count=Count('id')
            ).order_by('-count')

            overview.update({
                'trend': {
                    'pass_rates': [
                        (item['passed'] / item['total'] * 100) if item['total'] > 0 else 0
                        for item in trend_data
                    ],
                    'issue_counts': [
                        item['total'] - item['passed']
                        for item in trend_data
                    ]
                },
                'issueTypes': [
                    {
                        'name': item['quality_check__0__issue_type'] or '未分类',
                        'count': item['count']
                    }
                    for item in issue_types
                ],
                'causes': [
                    {
                        'name': item['quality_check__0__cause'] or '未知原因',
                        'value': item['count']
                    }
                    for item in causes
                ]
            })

            return Response(overview)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SalesDetailsView(APIView):
    """销售明细数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础查询
            queryset = SalesRecord.objects.select_related(
                'batch', 'batch__product', 'batch__product__category'
            ).all()
            
            # 添加过滤条件
            if date_from:
                queryset = queryset.filter(sale_date__gte=date_from)
            if date_to:
                queryset = queryset.filter(sale_date__lte=date_to)
            if category:
                queryset = queryset.filter(batch__product__category_id=category)

            # 分页
            total = queryset.count()
            start = (page - 1) * page_size
            end = start + page_size
            records = queryset[start:end]

            # 格式化数据
            data = {
                'count': total,
                'results': [{
                    'id': record.id,
                    'date': record.sale_date,
                    'product_name': record.batch.product.name,
                    'category_name': record.batch.product.category.name,
                    'batch_number': record.batch.batch_number,
                    'quantity': record.quantity,
                    'unit_price': float(record.unit_price),
                    'total_amount': float(record.total_amount),
                    'customer_name': record.customer_name
                } for record in records]
            }

            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TracingIssuesView(APIView):
    """追溯问题数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础查询
            batches = Batch.objects.select_related(
                'product', 'product__category'
            ).filter(
                production_records__isnull=True,
                logistics_records__isnull=True,
                sales_records__isnull=True
            ).distinct()
            
            # 添加过滤条件
            if date_from:
                batches = batches.filter(created_at__gte=date_from)
            if date_to:
                batches = batches.filter(created_at__lte=date_to)
            if category:
                batches = batches.filter(product__category_id=category)

            # 分页
            total = batches.count()
            start = (page - 1) * page_size
            end = start + page_size
            records = batches[start:end]

            # 格式化数据
            data = {
                'count': total,
                'results': [{
                    'id': batch.id,
                    'batch_number': batch.batch_number,
                    'product_name': batch.product.name,
                    'category_name': batch.product.category.name,
                    'created_at': batch.created_at,
                    'missing_records': {
                        'production': batch.production_records.exists(),
                        'logistics': batch.logistics_records.exists(),
                        'sales': batch.sales_records.exists()
                    }
                } for batch in records]
            }

            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QualityIssuesView(APIView):
    """质量问题数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 获取查询参数
            date_from = request.query_params.get('date_from')
            date_to = request.query_params.get('date_to')
            category = request.query_params.get('category')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 10))
            
            # 构建基础查询
            records = ProductionRecord.objects.select_related(
                'batch', 'batch__product', 'operator'
            ).filter(
                quality_check__0__result='failed'
            )
            
            # 添加过滤条件
            if date_from:
                records = records.filter(production_date__gte=date_from)
            if date_to:
                records = records.filter(production_date__lte=date_to)
            if category:
                records = records.filter(batch__product__category_id=category)

            # 分页
            total = records.count()
            start = (page - 1) * page_size
            end = start + page_size
            records = records[start:end]

            # 格式化数据
            data = {
                'count': total,
                'results': [{
                    'id': record.id,
                    'batch_number': record.batch.batch_number,
                    'product_name': record.batch.product.name,
                    'production_date': record.production_date,
                    'operator_name': record.operator.username,
                    'issue_type': record.quality_check[0].get('issue_type'),
                    'description': record.quality_check[0].get('description'),
                    'severity': record.quality_check[0].get('severity'),
                    'status': record.quality_check[0].get('status')
                } for record in records]
            }

            return Response(data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SalesExportView(APIView):
    """销售数据导出"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 创建工作簿
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('销售明细')
            
            # 设置表头样式
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            # 写入表头
            headers = ['日期', '商品名称', '分类', '批次号', '数量', '单价', '金额', '客户名称']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # 获取数据
            queryset = SalesRecord.objects.select_related(
                'batch', 'batch__product', 'batch__product__category'
            ).all()
            
            # 写入数据
            for row, record in enumerate(queryset, 1):
                worksheet.write(row, 0, record.sale_date.strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.write(row, 1, record.batch.product.name)
                worksheet.write(row, 2, record.batch.product.category.name)
                worksheet.write(row, 3, record.batch.batch_number)
                worksheet.write(row, 4, record.quantity)
                worksheet.write(row, 5, float(record.unit_price))
                worksheet.write(row, 6, float(record.total_amount))
                worksheet.write(row, 7, record.customer_name)
            
            workbook.close()
            
            # 返回Excel文件
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=sales_report.xlsx'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TracingExportView(APIView):
    """追溯数据导出"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 创建工作簿
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('追溯问题')
            
            # 设置表头样式
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            # 写入表头
            headers = ['批次号', '商品名称', '创建时间', '缺失生产记录', '缺失物流记录', '缺失销售记录']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # 获取数据
            batches = Batch.objects.select_related(
                'product'
            ).filter(
                production_records__isnull=True,
                logistics_records__isnull=True,
                sales_records__isnull=True
            ).distinct()
            
            # 写入数据
            for row, batch in enumerate(batches, 1):
                worksheet.write(row, 0, batch.batch_number)
                worksheet.write(row, 1, batch.product.name)
                worksheet.write(row, 2, batch.created_at.strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.write(row, 3, '是' if not batch.production_records.exists() else '否')
                worksheet.write(row, 4, '是' if not batch.logistics_records.exists() else '否')
                worksheet.write(row, 5, '是' if not batch.sales_records.exists() else '否')
            
            workbook.close()
            
            # 返回Excel文件
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=tracing_report.xlsx'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QualityExportView(APIView):
    """质量数据导出"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # 创建工作簿
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('质量问题')
            
            # 设置表头样式
            header_format = workbook.add_format({
                'bold': True,
                'align': 'center',
                'valign': 'vcenter',
                'border': 1
            })
            
            # 写入表头
            headers = ['批次号', '商品名称', '生产日期', '操作员', '问题类型', '问题描述', '严重程度', '状态']
            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
            
            # 获取数据
            records = ProductionRecord.objects.select_related(
                'batch', 'batch__product', 'operator'
            ).filter(
                quality_check__0__result='failed'
            )
            
            # 写入数据
            for row, record in enumerate(records, 1):
                worksheet.write(row, 0, record.batch.batch_number)
                worksheet.write(row, 1, record.batch.product.name)
                worksheet.write(row, 2, record.production_date.strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.write(row, 3, record.operator.username)
                worksheet.write(row, 4, record.quality_check[0].get('issue_type', ''))
                worksheet.write(row, 5, record.quality_check[0].get('description', ''))
                worksheet.write(row, 6, record.quality_check[0].get('severity', ''))
                worksheet.write(row, 7, record.quality_check[0].get('status', ''))
            
            workbook.close()
            
            # 返回Excel文件
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=quality_report.xlsx'
            
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
