from django.urls import path,include
from .views import (
    ItemDetailView,
    CheckoutView, 
    PaymentView,
    HomeView,
    SportswearView,
    CasualswearView,
    ClassywearView,
    OrderSummary,
    add_to_cart,
    remove_from_cart,
    remove_one_item_from_cart,
    SearchResultsView,
    add_discount_code
)

app_name = 'core'
urlpatterns= [
    path('', HomeView.as_view(), name='home-page'),
    path('sportswear/', SportswearView.as_view(), name='sportswear'),
    path('casualwear/', CasualswearView.as_view(), name='casualwear'),
    path('classywear/', ClassywearView.as_view(), name='classywear'),
    path('product-page/<slug>/', ItemDetailView.as_view(), name='product-page'),
    path('checkout-page/',CheckoutView.as_view(),name='checkout-page'),
    path('payment-page/<payment_options>/', PaymentView.as_view(), name='payment-page'),
    path('order-summary/', OrderSummary.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-one-item-from-cart/<slug>/', remove_one_item_from_cart, name='remove-one-item-from-cart'),
    path('search_results/', SearchResultsView.as_view(), name='search_results'),
    path('add_discount_code/', add_discount_code, name='add_discount_code'),
]

