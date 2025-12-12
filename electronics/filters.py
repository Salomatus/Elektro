import django_filters
from .models import NetworkNode


class NetworkNodeFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name='contact__country',
        lookup_expr='icontains',
        label='Страна'
    )
    city = django_filters.CharFilter(
        field_name='contact__city',
        lookup_expr='icontains',
        label='Город'
    )
    node_type = django_filters.ChoiceFilter(
        choices=NetworkNode.NODE_TYPES,
        label='Тип узла'
    )

    class Meta:
        model = NetworkNode
        fields = ['country', 'city', 'node_type']
