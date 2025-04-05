from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, MaterialViewSet, MaterialBatchViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'batches', MaterialBatchViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 