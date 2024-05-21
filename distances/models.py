from django.db import models

from foodcartapp.models import Restaurant


class Distance(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='distances',
        verbose_name='Ресторан'
    )
    order_address = models.CharField(
        verbose_name='Адрес заказа',
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )
    distance = models.FloatField(
        blank=True,
        null=True,
        verbose_name='Расстояние'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Время обновления'
    )

    class Meta:
        verbose_name = 'Расстояние'
        verbose_name_plural = 'Расстояния'
        ordering = ['distance']
        unique_together = (
            ('restaurant', 'order_address'),
        )
