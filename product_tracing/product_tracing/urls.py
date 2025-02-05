# product_tracing/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/tracing/', include('tracing.urls')),
    path('api/analysis/', include('data_analysis.urls')),
    path('api/dashboard/', include('dashboard_app.urls')),
]