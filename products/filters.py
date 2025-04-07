import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    size = django_filters.CharFilter(field_name="variants__size", lookup_expr='iexact')
    color = django_filters.CharFilter(field_name="variants__color", lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')  # Greater than or equal to
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')  # Less than or equal to

    class Meta:
        model = Product
        fields = ['category__slug', 'tags', 'variants__size', 'variants__color', 'min_price', 'max_price']
