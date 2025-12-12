from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date

from .models import Contact, Product, NetworkNode


class ContactModelTest(TestCase):
    """Тесты для модели Contact"""

    def setUp(self):
        self.contact_data = {
            'email': 'test@example.com',
            'country': 'Россия',
            'city': 'Москва',
            'street': 'Ленина',
            'house_number': '10'
        }

    def test_create_contact(self):
        """Тест создания контакта"""
        contact = Contact.objects.create(**self.contact_data)
        self.assertEqual(contact.email, 'test@example.com')
        self.assertEqual(contact.country, 'Россия')
        self.assertEqual(contact.city, 'Москва')
        self.assertEqual(contact.street, 'Ленина')
        self.assertEqual(contact.house_number, '10')

    def test_contact_str_representation(self):
        """Тест строкового представления контакта"""
        contact = Contact.objects.create(**self.contact_data)
        expected_str = "Россия, Москва, Ленина, 10"
        self.assertEqual(str(contact), expected_str)

    def test_contact_verbose_names(self):
        """Тест verbose names"""
        self.assertEqual(Contact._meta.verbose_name, 'Контакт')
        self.assertEqual(Contact._meta.verbose_name_plural, 'Контакты')


class ProductModelTest(TestCase):
    """Тесты для модели Product"""

    def setUp(self):
        self.product_data = {
            'name': 'Смартфон',
            'model': 'Galaxy S21',
            'release_date': date(2021, 1, 1)
        }

    def test_create_product(self):
        """Тест создания продукта"""
        product = Product.objects.create(**self.product_data)
        self.assertEqual(product.name, 'Смартфон')
        self.assertEqual(product.model, 'Galaxy S21')
        self.assertEqual(product.release_date, date(2021, 1, 1))

    def test_product_str_representation(self):
        """Тест строкового представления продукта"""
        product = Product.objects.create(**self.product_data)
        expected_str = "Смартфон Galaxy S21"
        self.assertEqual(str(product), expected_str)

    def test_product_verbose_names(self):
        """Тест verbose names"""
        self.assertEqual(Product._meta.verbose_name, 'Продукт')
        self.assertEqual(Product._meta.verbose_name_plural, 'Продукты')


class NetworkNodeModelTest(TestCase):
    """Тесты для модели NetworkNode"""

    def setUp(self):
        # Создаем тестовые данные
        self.contact1 = Contact.objects.create(
            email='factory@example.com',
            country='Россия',
            city='Москва',
            street='Заводская',
            house_number='1'
        )

        self.contact2 = Contact.objects.create(
            email='retail@example.com',
            country='Россия',
            city='Санкт-Петербург',
            street='Розничная',
            house_number='2'
        )

        self.contact3 = Contact.objects.create(
            email='entrepreneur@example.com',
            country='Россия',
            city='Казань',
            street='Предпринимательская',
            house_number='3'
        )

        self.product1 = Product.objects.create(
            name='Ноутбук',
            model='ThinkPad',
            release_date=date(2022, 1, 1)
        )

        self.product2 = Product.objects.create(
            name='Монитор',
            model='UltraSharp',
            release_date=date(2023, 1, 1)
        )

    def test_create_factory(self):
        """Тест создания завода"""
        factory = NetworkNode.objects.create(
            name='Завод Электроника',
            node_type='factory',
            contact=self.contact1,
            debt=Decimal('0.00')
        )
        factory.products.add(self.product1, self.product2)

        self.assertEqual(factory.name, 'Завод Электроника')
        self.assertEqual(factory.node_type, 'factory')
        self.assertEqual(factory.contact, self.contact1)
        self.assertEqual(factory.debt, Decimal('0.00'))
        self.assertEqual(factory.products.count(), 2)
        self.assertIsNone(factory.supplier)

    def test_create_retail_network(self):
        """Тест создания розничной сети с поставщиком"""
        # Сначала создаем завод
        factory = NetworkNode.objects.create(
            name='Завод Электроника',
            node_type='factory',
            contact=self.contact1
        )

        # Затем розничную сеть с заводом как поставщиком
        retail = NetworkNode.objects.create(
            name='Розничная сеть ТехноМир',
            node_type='retail',
            contact=self.contact2,
            supplier=factory,
            debt=Decimal('150000.50')
        )

        self.assertEqual(retail.name, 'Розничная сеть ТехноМир')
        self.assertEqual(retail.node_type, 'retail')
        self.assertEqual(retail.supplier, factory)
        self.assertEqual(retail.debt, Decimal('150000.50'))

    def test_create_entrepreneur(self):
        """Тест создания индивидуального предпринимателя"""
        # Создаем цепочку: Завод -> Розничная сеть -> ИП
        factory = NetworkNode.objects.create(
            name='Завод Электроника',
            node_type='factory',
            contact=self.contact1
        )

        retail = NetworkNode.objects.create(
            name='Розничная сеть ТехноМир',
            node_type='retail',
            contact=self.contact2,
            supplier=factory
        )

        entrepreneur = NetworkNode.objects.create(
            name='ИП Иванов',
            node_type='entrepreneur',
            contact=self.contact3,
            supplier=retail,
            debt=Decimal('50000.75')
        )

        self.assertEqual(entrepreneur.name, 'ИП Иванов')
        self.assertEqual(entrepreneur.node_type, 'entrepreneur')
        self.assertEqual(entrepreneur.supplier, retail)

    def test_factory_cannot_have_supplier(self):
        """Тест, что завод не может иметь поставщика"""
        with self.assertRaises(ValidationError):
            factory_with_supplier = NetworkNode(
                name='Завод с поставщиком',
                node_type='factory',
                contact=self.contact1,
                supplier=NetworkNode.objects.create(
                    name='Другой завод',
                    node_type='factory',
                    contact=self.contact2
                )
            )
            factory_with_supplier.clean()

    def test_entrepreneur_cannot_be_supplier(self):
        """Тест, что ИП не может быть поставщиком"""
        entrepreneur = NetworkNode.objects.create(
            name='ИП Поставщик',
            node_type='entrepreneur',
            contact=self.contact3
        )

        with self.assertRaises(ValidationError):
            retail_with_entrepreneur_supplier = NetworkNode(
                name='Розничная сеть',
                node_type='retail',
                contact=self.contact2,
                supplier=entrepreneur
            )
            retail_with_entrepreneur_supplier.clean()

    def test_circular_reference_prevention(self):
        """Тест предотвращения циклических ссылок"""
        factory = NetworkNode.objects.create(
            name='Завод',
            node_type='factory',
            contact=self.contact1
        )

        retail = NetworkNode.objects.create(
            name='Розничная сеть',
            node_type='retail',
            contact=self.contact2,
            supplier=factory
        )

        entrepreneur = NetworkNode.objects.create(
            name='ИП',
            node_type='entrepreneur',
            contact=self.contact3,
            supplier=retail
        )

        # Пытаемся создать циклическую ссылку
        with self.assertRaises(ValidationError):
            factory.supplier = entrepreneur
            factory.clean()

    def test_self_supplier_prevention(self):
        """Тест предотвращения ссылки на самого себя"""
        factory = NetworkNode(
            name='Завод',
            node_type='factory',
            contact=self.contact1
        )

        with self.assertRaises(ValidationError):
            factory.supplier = factory
            factory.clean()

    def test_hierarchy_level_calculation(self):
        """Тест расчета уровня иерархии"""
        factory = NetworkNode.objects.create(
            name='Завод',
            node_type='factory',
            contact=self.contact1
        )

        retail = NetworkNode.objects.create(
            name='Розничная сеть',
            node_type='retail',
            contact=self.contact2,
            supplier=factory
        )

        entrepreneur = NetworkNode.objects.create(
            name='ИП',
            node_type='entrepreneur',
            contact=self.contact3,
            supplier=retail
        )

        self.assertEqual(factory.hierarchy_level, 0)
        self.assertEqual(retail.hierarchy_level, 1)
        self.assertEqual(entrepreneur.hierarchy_level, 2)

    def test_negative_debt_validation(self):
        """Тест валидации отрицательной задолженности"""
        with self.assertRaises(ValidationError):
            factory = NetworkNode(
                name='Завод',
                node_type='factory',
                contact=self.contact1,
                debt=Decimal('-100.00')
            )
            factory.full_clean()

    def test_node_str_representation(self):
        """Тест строкового представления узла сети"""
        factory = NetworkNode.objects.create(
            name='Электронный завод',
            node_type='factory',
            contact=self.contact1
        )

        expected_str = "Завод: Электронный завод"
        self.assertEqual(str(factory), expected_str)

    def test_network_node_verbose_names(self):
        """Тест verbose names для NetworkNode"""
        self.assertEqual(NetworkNode._meta.verbose_name, 'Узел сети')
        self.assertEqual(NetworkNode._meta.verbose_name_plural, 'Узлы сети')

    def test_ordering(self):
        """Тест ordering в Meta классе"""
        factory1 = NetworkNode.objects.create(
            name='Завод 1',
            node_type='factory',
            contact=self.contact1
        )

        factory2 = NetworkNode.objects.create(
            name='Завод 2',
            node_type='factory',
            contact=self.contact2
        )

        nodes = NetworkNode.objects.all()
        self.assertEqual(nodes[0], factory2)
        self.assertEqual(nodes[1], factory1)

    def test_products_relationship(self):
        """Тест связи ManyToMany с продуктами"""
        factory = NetworkNode.objects.create(
            name='Завод',
            node_type='factory',
            contact=self.contact1
        )

        factory.products.add(self.product1)
        factory.products.add(self.product2)

        self.assertEqual(factory.products.count(), 2)
        self.assertIn(self.product1, factory.products.all())
        self.assertIn(self.product2, factory.products.all())

    def test_supplier_relationship(self):
        """Тест связи ForeignKey с самим собой"""
        factory = NetworkNode.objects.create(
            name='Завод',
            node_type='factory',
            contact=self.contact1
        )

        retail = NetworkNode.objects.create(
            name='Розничная сеть',
            node_type='retail',
            contact=self.contact2,
            supplier=factory
        )

        # Проверяем обратную связь
        self.assertIn(retail, factory.children.all())
