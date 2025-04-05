# tracing/urls.py

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # 商品分类
    path('categories/', views.CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view()),

    # 商品管理
    path('list/', views.ProductListCreateView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view()),  # GET 详情, PUT 更新, DELETE 删除

    # 批次管理
    path('batches/', views.BatchListCreateView.as_view(), name='batch-list'),
    path('batches/<int:pk>/', views.BatchDetailView.as_view()),
    path('batches/<int:pk>/materials/', views.BatchMaterialsView.as_view(), name='batch-materials'),
    # path('qrcode/<str:batch_number>/', views.generate_qrcode, name='batch-qrcode'),
    # path('qrcode/<str:batch_number>/generate/', views.generate_qrcode, name='generate_qrcode'),

    # 图片上传
    path('upload-image/', views.ProductImageUploadView.as_view(), name='product-image-upload'),
]