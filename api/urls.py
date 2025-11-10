from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NetworkNodeViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'nodes', NetworkNodeViewSet, basename='node')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('v1/', include(router.urls)),
]