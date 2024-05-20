from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        ACCEPTED = 'Accepted', _('Принят')
        COOKING = 'Cooking', _('Готовится')
        DELIVERING = 'Delivering', _('В пути')
        DELIVERED = 'Delivered', _('Доставлен')

    client_name = models.CharField(
        max_length=50,
        verbose_name='Имя'
    )
    client_lastname = models.CharField(
        max_length=50,
        verbose_name='Фамилия'
    )
    phone = PhoneNumberField(
        verbose_name='Телефон'
    )
    address = models.CharField(
        max_length=100,
        verbose_name='Адрес доставки'
    )
    status = models.CharField(
        choices=StatusChoices.choices,
        default=StatusChoices.ACCEPTED,
        max_length=10,
        db_index=True,
        verbose_name='Статус'
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name='Комментарий'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.address

    @property
    def client_full_name(self):
        return f"{self.client_name} {self.client_lastname}"


class OrderProduct(models.Model):
    order = models.ForeignKey(
        to=Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='products'
    )
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name='Стоимость'
    )

    class Meta:
        verbose_name = 'Товар Заказа'
        verbose_name_plural = 'Товары Заказов'

    def __str__(self):
        return f"{self.order}"

    def set_price(self):
        self.price = self.product.price
