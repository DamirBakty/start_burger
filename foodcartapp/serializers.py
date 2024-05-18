from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from foodcartapp.models import Order, OrderProduct


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = (
            'order',
            'product',
            'quantity'
        )


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)
    firstname = serializers.CharField(source='client_name')
    lastname = serializers.CharField(source='client_lastname')
    phonenumber = PhoneNumberField(source='phone')

    class Meta:
        model = Order
        fields = (
            'firstname',
            'lastname',
            'address',
            'phonenumber',
            'products'
        )


    def validate_products(self, value):
        if not value:
            raise serializers.ValidationError("Это поле не может быть пустым")
        return value

    def create(self, validated_data):
        order_products_details = validated_data.pop('products')
        order = Order.objects.create(
            client_name=validated_data['client_name'],
            client_lastname=validated_data['client_lastname'],
            phone=validated_data['phone'],
            address=validated_data['address']
        )
        order_products = [
            OrderProduct(order=order, **product_data) for product_data in order_products_details
        ]
        OrderProduct.objects.bulk_create(order_products)
        return order
