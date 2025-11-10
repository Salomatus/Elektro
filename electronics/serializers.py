from rest_framework import serializers
from .models import Contact, Product, NetworkNode


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class NetworkNodeSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    hierarchy_level = serializers.ReadOnlyField()

    class Meta:
        model = NetworkNode
        fields = [
            'id', 'name', 'node_type', 'contact', 'products',
            'supplier', 'supplier_name', 'debt', 'created_at', 'hierarchy_level'
        ]
        read_only_fields = ['debt']  # Запрещаем обновление через API

    def create(self, validated_data):
        contact_data = validated_data.pop('contact')
        products_data = validated_data.pop('products', [])

        contact = Contact.objects.create(**contact_data)
        node = NetworkNode.objects.create(contact=contact, **validated_data)

        if products_data:
            node.products.set(products_data)

        return node

    def update(self, instance, validated_data):
        contact_data = validated_data.pop('contact', None)
        products_data = validated_data.pop('products', None)

        # Обновляем контактную информацию
        if contact_data:
            contact_serializer = ContactSerializer(
                instance.contact,
                data=contact_data,
                partial=True
            )
            if contact_serializer.is_valid():
                contact_serializer.save()

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем продукты
        if products_data is not None:
            instance.products.set(products_data)

        return instance


class NetworkNodeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания с вложенным контактом"""
    contact = ContactSerializer()

    class Meta:
        model = NetworkNode
        fields = ['name', 'node_type', 'contact', 'supplier', 'products']


class NetworkNodeUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления без поля debt"""
    contact = ContactSerializer()

    class Meta:
        model = NetworkNode
        fields = ['name', 'node_type', 'contact', 'supplier', 'products']