from django import template

from distances.models import Distance

register = template.Library()


@register.filter(name='get_restaurant_distance')
def get_restaurant_distance(restaurant, order_address):
    try:
        distance = Distance.objects.get(
            restaurant=restaurant,
            order_address=order_address
        )
        return distance.distance
    except Distance.DoesNotExist:
        return 'Не найдено'
