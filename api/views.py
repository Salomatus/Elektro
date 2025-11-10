from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

import electronics
from electronics.models import NetworkNode, Product
from electronics.serializers import (
    NetworkNodeSerializer,
    NetworkNodeCreateSerializer,
    NetworkNodeUpdateSerializer,
    ProductSerializer
)
from electronics.filters import NetworkNodeFilter
from electronics.permissions import IsActiveEmployee


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet для продуктов"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsActiveEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'model']


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """ViewSet для узлов сети"""
    queryset = NetworkNode.objects.select_related('contact', 'supplier').prefetch_related('products')
    permission_classes = [IsAuthenticated, IsActiveEmployee]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NetworkNodeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return NetworkNodeCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return NetworkNodeUpdateSerializer
        return NetworkNodeSerializer

    def perform_create(self, serializer):
        """Создание узла сети"""
        serializer.save()

    def perform_update(self, serializer):
        """Обновление узла сети (исключаем поле debt)"""
        serializer.save()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по сети"""
        total_nodes = NetworkNode.objects.count()
        factories = NetworkNode.objects.filter(node_type='factory').count()
        retailers = NetworkNode.objects.filter(node_type='retail').count()
        entrepreneurs = NetworkNode.objects.filter(node_type='entrepreneur').count()

        total_debt = NetworkNode.objects.aggregate(total_debt=electronics.models.Sum('debt'))['total_debt'] or 0

        return Response({
            'total_nodes': total_nodes,
            'factories': factories,
            'retailers': retailers,
            'entrepreneurs': entrepreneurs,
            'total_debt': float(total_debt),
        })

    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        """Получение иерархии для конкретного узла"""
        node = self.get_object()

        hierarchy_chain = []
        current = node
        while current:
            hierarchy_chain.append({
                'id': current.id,
                'name': current.name,
                'type': current.get_node_type_display(),
                'level': current.hierarchy_level
            })
            current = current.supplier

        return Response({
            'current_node': {
                'id': node.id,
                'name': node.name,
                'type': node.get_node_type_display(),
                'level': node.hierarchy_level
            },
            'hierarchy_chain': list(reversed(hierarchy_chain))
        })