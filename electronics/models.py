from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User


class Contact(models.Model):
    """Контактная информация"""
    email = models.EmailField(verbose_name='Email')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house_number = models.CharField(max_length=10, verbose_name='Номер дома')

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f"{self.country}, {self.city}, {self.street}, {self.house_number}"


class Product(models.Model):
    """Продукт/Товар"""
    name = models.CharField(max_length=255, verbose_name='Название')
    model = models.CharField(max_length=255, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f"{self.name} {self.model}"


class NetworkNode(models.Model):
    """Узлы сети (Завод, Розничная сеть, Индивидуальный предприниматель)"""

    NODE_TYPES = [
        ('factory', 'Завод'),
        ('retail', 'Розничная сеть'),
        ('entrepreneur', 'Индивидуальный предприниматель'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название')
    node_type = models.CharField(
        max_length=20,
        choices=NODE_TYPES,
        verbose_name='Тип узла'
    )
    contact = models.OneToOneField(
        Contact,
        on_delete=models.CASCADE,
        verbose_name='Контактная информация'
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        verbose_name='Продукты'
    )
    supplier = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Поставщик'
    )
    debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Задолженность перед поставщиком'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')

    class Meta:
        verbose_name = 'Узел сети'
        verbose_name_plural = 'Узлы сети'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.name}"

    @property
    def hierarchy_level(self):
        """Определение уровня иерархии"""
        if self.node_type == 'factory':
            return 0
        if not self.supplier:
            return 0

        level = 1
        current = self.supplier
        while current:
            if current.node_type == 'factory':
                return level
            level += 1
            current = current.supplier
        return level

    def clean(self):
        from django.core.exceptions import ValidationError

        # Завод не может иметь поставщика
        if self.node_type == 'factory' and self.supplier:
            raise ValidationError('Завод не может иметь поставщика')

        # Валидация иерархии
        if self.supplier:
            if self.supplier.node_type == 'entrepreneur':
                raise ValidationError('Поставщиком не может быть индивидуальный предприниматель')

            # Предотвращение циклических ссылок
            visited = set()
            current = self.supplier
            while current:
                if current.id in visited:
                    raise ValidationError('Обнаружена циклическая ссылка в цепочке поставщиков')
                visited.add(current.id)
                if current == self:
                    raise ValidationError('Узел не может быть своим собственным поставщиком')
                current = current.supplier

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)