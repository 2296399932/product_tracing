from django.contrib import admin
from django.urls import path, include
from . import views
# data_analysis/urls.py
urlpatterns = [
    # 销售统计
    path('sales/statistics/', views.SalesStatisticsView.as_view()),  # GET: 获取销售统计数据

    path('sales/trend/', views.SalesTrendView.as_view()),           # GET: 获取销售趋势数据
    path('sales/ranking/', views.SalesRankingView.as_view()),       # GET: 获取销售排行数据
    
    # 追溯统计
    path('tracing/statistics/', views.TracingStatisticsView.as_view()), # GET: 获取追溯统计数据
    path('tracing/regions/', views.TracingRegionView.as_view()),        # GET: 获取地区追溯分布
    
    # 质量分析
    path('quality/', views.QualityAnalysisListView.as_view()),         # GET: 获取质量分析列表
                                                                       # POST: 创建质量分析记录
    path('quality/<int:pk>/', views.QualityAnalysisDetailView.as_view()), # GET: 获取质量分析详情
    path('quality/report/', views.QualityReportView.as_view()),           # GET: 获取质量分析报告

    path('sales/', views.SalesAnalysisView.as_view()),                     # ✓
    path('tracing/', views.TracingAnalysisView.as_view()),                 # ✓
    path('quality/', views.QualityAnalysisView.as_view()),                 # ✓

    path('export/', views.AnalysisExportView.as_view()),  # 导出分析报告
]