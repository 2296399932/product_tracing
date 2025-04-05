from django.urls import path
from . import views


# tracing/urls.py
urlpatterns = [
    path('production/', views.ProductionRecordListCreateView.as_view()),
    path('production/<int:pk>/', views.ProductionRecordDetailView.as_view()),
    path('logistics/', views.LogisticsRecordListCreateView.as_view()),
    path('logistics/<int:pk>/', views.LogisticsRecordDetailView.as_view()),
    path('sales/', views.SalesRecordListCreateView.as_view()),
    path('sales/<int:pk>/', views.SalesRecordDetailView.as_view()),
    path('trace/<str:batch_number>/', views.TraceView.as_view(), name='trace-detail'),
    path('trace/scan/<str:qr_code>/', views.TraceScanView.as_view()),
    path('search-batches/', views.search_batches, name='search-batches'),
    path('recent-batches/', views.recent_batches, name='recent-batches'),
    path('qrcode/<str:batch_number>/', views.QRCodeView.as_view(), name='generate_qrcode'),
path('qrcode/<str:batch_number>/generate/',views.QRCodeView.as_view(), name='generate_qrcode'),
    path('public-trace/<str:qr_code>/', views.PublicTraceView.as_view(), name='public-trace'),
    path('public-page/<str:batch_number>/', views.public_trace_page, name='public-trace-page'),
    path('health-check/', views.health_check, name='health-check'),
    path('test-connection/', views.test_connection, name='test-connection'),
]