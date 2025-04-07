from rest_framework import generics, permissions
from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer, OrderSerializer
from utils.custom_response import success_response
from products.models import Product
from utils.custom_response import success_response, error_response
from .models import WishlistItem
from .serializers import WishlistItemSerializer

class CartView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Cart fetched")

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response(message="Product does not exist")

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return success_response(CartItemSerializer(cart_item).data, "Item added to cart")

class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        item = CartItem.objects.filter(user=request.user, pk=pk).first()
        if item:
            item.delete()
            return success_response(message="Item removed from cart")
        return success_response(message="Item not found")

class CheckoutView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return success_response(data=None, message="Cart is empty")

        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=request.user, total_price=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        cart_items.delete()

        return success_response(OrderSerializer(order).data, "Order placed")

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Orders retrieved")

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(order)
        return success_response(serializer.data, "Order detail retrieved")


class WishlistView(generics.ListAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, "Wishlist fetched")

class AddToWishlistView(generics.CreateAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return error_response(message="Product does not exist")

        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user, product=product
        )
        if created:
            return success_response(WishlistItemSerializer(wishlist_item).data, "Item added to wishlist")
        return error_response(message="Item already in wishlist")

class RemoveFromWishlistView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        # Ensure the item belongs to the authenticated user
        item = WishlistItem.objects.filter(user=request.user, pk=pk).first()
        
        if item:
            item.delete()  # Delete the item
            return success_response(message="Item removed from wishlist")
        
        # Return error if item doesn't exist
        return error_response(message="Item not found")
