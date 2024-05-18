from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from foodcartapp.models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = (
            'id',
            'order',
            'product',
            'quantity',
            'price'
        )
        extra_kwargs = {
            'order': {'read_only': True},
            'price': {'read_only': True},
        }


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False)
    firstname = serializers.CharField(source='client_name')
    lastname = serializers.CharField(source='client_lastname')
    phonenumber = PhoneNumberField(source='phone')

    class Meta:
        model = Order
        fields = (
            'id',
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products'
        )

    @transaction.atomic
    def create(self, validated_data):
        order_products_details = validated_data.pop('products')
        order = Order.objects.create(
            client_name=validated_data['client_name'],
            client_lastname=validated_data['client_lastname'],
            phone=validated_data['phone'],
            address=validated_data['address']
        )
        order_products = []
        for product_data in order_products_details:
            order_product = OrderProduct(order=order, **product_data)
            order_product.set_price()
            order_products.append(order_product)
        OrderProduct.objects.bulk_create(order_products)
        return order
