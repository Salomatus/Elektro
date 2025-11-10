from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from .models import Contact, Product, NetworkNode


class CityFilter(admin.SimpleListFilter):
    """Фильтр по названию города"""
    title = 'Город'
    parameter_name = 'city'

    def lookups(self, request, model_admin):
        cities = Contact.objects.values_list('city', flat=True).distinct()
        return [(city, city) for city in cities if city]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(contact__city=self.value())
        return queryset


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'country', 'city', 'street', 'house_number']
    list_filter = ['country', 'city']
    search_fields = ['email', 'country', 'city', 'street']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'model', 'release_date']
    list_filter = ['release_date']
    search_fields = ['name', 'model']


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_node_type_display',
        'hierarchy_level_display',
        'supplier_link',
        'city_display',
        'debt',
        'created_at'
    ]
    list_filter = ['node_type', CityFilter, 'created_at']
    search_fields = ['name', 'contact__email', 'contact__city']
    readonly_fields = ['created_at', 'hierarchy_level_display']
    list_editable = ['debt']
    actions = ['clear_debt']
    filter_horizontal = ['products']

    def supplier_link(self, obj):
        if obj.supplier:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/electronics/networknode/{obj.supplier.id}/change/',
                obj.supplier.name
            )
        return "-"
    supplier_link.short_description = 'Поставщик'

    def city_display(self, obj):
        return obj.contact.city
    city_display.short_description = 'Город'

    def hierarchy_level_display(self, obj):
        return obj.hierarchy_level
    hierarchy_level_display.short_description = 'Уровень иерархии'

    def clear_debt(self, request, queryset):
        """Admin action для очистки задолженности"""
        updated = queryset.update(debt=0)
        self.message_user(
            request,
            f'Задолженность очищена для {updated} объектов'
        )
    clear_debt.short_description = "Очистить задолженность перед поставщиком"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('contact', 'supplier')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "supplier":
            # Исключаем предпринимателей из возможных поставщиков
            kwargs["queryset"] = NetworkNode.objects.filter(
                Q(node_type='factory') | Q(node_type='retail')
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'node_type', 'contact', 'products')
        }),
        ('Поставщик и финансы', {
            'fields': ('supplier', 'debt')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'hierarchy_level_display'),
            'classes': ('collapse',)
        }),
    )