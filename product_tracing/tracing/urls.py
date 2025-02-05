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
    path('trace/<str:batch_number>/', views.trace_batch, name='trace-batch'),
    path('trace/scan/<str:qr_code>/', views.TraceScanView.as_view()),
    path('search-batches/', views.search_batches, name='search-batches'),
    path('recent-batches/', views.recent_batches, name='recent-batches'),
]