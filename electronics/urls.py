from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('nodes/<int:pk>/', views.node_detail, name='node_detail'),
    path('products/', views.product_list, name='product_list'),
    path('contacts/', views.contact_list, name='contact_list'),
]
