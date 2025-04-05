# product_tracing/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# 简单的健康检查视图
def health_check(request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/tracing/', include('tracing.urls')),
    path('api/materials/', include('materials.urls')),
    path('api/analysis/', include('data_analysis.urls')),
    path('api/dashboard/', include('dashboard_app.urls')),
    # 添加健康检查端点
    path('api/health-check/', health_check, name='health_check'),
]

# 添加这行来服务媒体文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)