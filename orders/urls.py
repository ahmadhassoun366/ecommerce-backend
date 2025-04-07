from django.urls import path
from . import views

urlpatterns = [
    path('cart', views.CartView.as_view(), name='cart-view'),
    path('cart/add', views.AddToCartView.as_view(), name='cart-add'),
    path('cart/remove/<int:pk>', views.RemoveFromCartView.as_view(), name='cart-remove'),
    path('orders', views.OrderListView.as_view(), name='order-list'),
    path('orders/checkout', views.CheckoutView.as_view(), name='checkout'),
    path('orders/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
    path('wishlist', views.WishlistView.as_view(), name='wishlist-view'),
    path('wishlist/add', views.AddToWishlistView.as_view(), name='add-to-wishlist'),
    path('wishlist/<int:pk>', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]
