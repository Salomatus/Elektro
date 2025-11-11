from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NetworkNodeViewSet,
    ProductViewSet,
    ContactViewSet,
    EmployeeViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'nodes', NetworkNodeViewSet, basename='node')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'contacts', ContactViewSet, basename='contact')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/', include(router.urls)),
]
