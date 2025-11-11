from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import NetworkNode, Product, Contact


def is_staff_user(user):
    return user.is_staff


def home(request):
    """Главная страница"""
    nodes = NetworkNode.objects.select_related('contact', 'supplier').prefetch_related('products')

    # Фильтрация
    node_type = request.GET.get('node_type')
    country = request.GET.get('country')
    city = request.GET.get('city')

    if node_type:
        nodes = nodes.filter(node_type=node_type)
    if country:
        nodes = nodes.filter(contact__country__icontains=country)
    if city:
        nodes = nodes.filter(contact__city__icontains=city)

    context = {
        'nodes': nodes,
        'total_nodes': nodes.count(),
        'node_types': NetworkNode.NODE_TYPES,
    }
    return render(request, 'electronics/home.html', context)


@login_required
@user_passes_test(is_staff_user)
def node_detail(request, pk):
    """Детальная информация об узле сети"""
    node = get_object_or_404(
        NetworkNode.objects.select_related('contact', 'supplier')
        .prefetch_related('products'),
        pk=pk
    )

    # Получаем иерархию
    hierarchy_chain = []
    current = node
    while current:
        hierarchy_chain.append(current)
        current = current.supplier

    context = {
        'node': node,
        'hierarchy_chain': list(reversed(hierarchy_chain)),
        'products': node.products.all(),
    }
    return render(request, 'electronics/node_detail.html', context)


def product_list(request):
    """Список всех продуктов"""
    products = Product.objects.all()

    # Фильтрация
    name = request.GET.get('name')
    if name:
        products = products.filter(name__icontains=name)

    context = {
        'products': products,
        'total_products': products.count()
    }
    return render(request, 'electronics/product_list.html', context)


def contact_list(request):
    """Список контактов"""
    contacts = Contact.objects.all()

    # Фильтрация
    country = request.GET.get('country')
    city = request.GET.get('city')

    if country:
        contacts = contacts.filter(country__icontains=country)
    if city:
        contacts = contacts.filter(city__icontains=city)

    context = {
        'contacts': contacts,
        'total_contacts': contacts.count()
    }
    return render(request, 'electronics/contact_list.html', context)
