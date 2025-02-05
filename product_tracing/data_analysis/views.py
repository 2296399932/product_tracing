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
