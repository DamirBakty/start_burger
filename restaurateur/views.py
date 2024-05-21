from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, F
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from distances.models import Distance
from foodcartapp.models import Product, Restaurant, Order
from foodcartapp.yandex_geo import fetch_coordinates, get_distance_km
from star_burger.settings import API_KEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.prefetch_related(
        'products'
    ).annotate(
        price_sum=Sum(F('products__quantity') * F('products__price'))
    ).exclude(
        status=Order.StatusChoices.DELIVERED,
    )

    restaurants = Restaurant.objects.prefetch_related(
        'menu_items',
        'menu_items__product',
        'distances'
    )

    for order in orders:
        order_products_ids = set(order.products.values_list('product_id', flat=True))
        available_restaurants = []
        order.products.select_related('product').filter(
            product__menu_items__product_id__in=order_products_ids,
        )

        for restaurant in restaurants:
            menu_products_ids = set(restaurant.menu_items.values_list('product_id', flat=True))
            if menu_products_ids.intersection(order_products_ids):
                try:
                    distance = Distance.objects.get(
                        restaurant=restaurant,
                        order_address=order.address,
                    )
                except Distance.DoesNotExist:
                    restaurant_coordinates = fetch_coordinates(API_KEY, restaurant.address)
                    order_coordinates = fetch_coordinates(API_KEY, order.address)
                    distance_in_km = get_distance_km(restaurant_coordinates, order_coordinates)
                    distance = Distance.objects.create(
                        restaurant=restaurant,
                        order_address=order.address,
                        distance=distance_in_km
                    )
                restaurant.distance = distance.distance
                available_restaurants.append(restaurant)

        available_restaurants = sorted(available_restaurants, key=lambda x: x.distance)
        order.available_restaurants = available_restaurants

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
        'currentUrl': request.path,
    })
