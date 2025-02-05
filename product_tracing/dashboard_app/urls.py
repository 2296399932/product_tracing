from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # 概览数据
    path('overview/', views.overview, name='dashboard-overview'),
    
    # 销售相关
    path('sales-trend/', views.sales_trend, name='sales-trend'),
    path('category-stats/', views.category_stats, name='category-stats'),
    path('latest-orders/', views.latest_orders, name='latest-orders'),
    
    # 预警信息
    path('warnings/', views.warnings, name='warnings'),
    path('warnings/<int:pk>/', views.DashboardWarningsView.as_view(), name='warning_detail'),
] 