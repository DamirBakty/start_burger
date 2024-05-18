from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    try:
        order_details = request.data
        order_product_details = order_details.get('products')

        if not order_product_details:
            return Response({
                'products': 'Это обязательно поле'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(order_product_details, list) and \
            not all(isinstance(item, dict) for item in order_product_details):
            return Response({
                'products': 'Неверный формат поля'
            }, status=status.HTTP_400_BAD_REQUEST)

        client_name = order_details.get('firstname')
        client_lastname = order_details.get('lastname')
        address = order_details.get('address')
        phone = order_details.get('phonenumber')

        if not isinstance(client_name, str):
            return Response({
                'firstname': 'Это поле должно содержать строку'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(client_lastname, str):
            return Response({
                'lastname': 'Это поле должно содержать строку'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(address, str):
            return Response({
                'address': 'Это поле должно содержать строку'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order(
                client_name=client_name,
                client_lastname=client_lastname,
                address=address,
                phone=phone
            )
            order.full_clean()
            order.save()
        except ValidationError as e:
            return Response(
                e.message_dict,
                status=status.HTTP_400_BAD_REQUEST
            )

        order_products = []

        for product_detail in order_product_details:
            product_id = product_detail.get('product')
            product = get_object_or_404(Product, id=product_id)

            quantity = product_detail.get('quantity')

            order_products.append(OrderProduct(
                order=order,
                product=product,
                quantity=quantity,
            ))

        OrderProduct.objects.bulk_create(order_products)

    except ValueError:
        return Response({
            'error': 'Неверный JSON',
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Заказ Создан"
    }, status=status.HTTP_201_CREATED)
