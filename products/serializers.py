from rest_framework import serializers
from .models import Product, ProductVariant, ProductImage

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'size', 'color', 'additional_price', 'stock']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    variants = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'stock',
            'tags', 'created_at', 'category', 'variants', 'images'
        ]

    def get_variants(self, obj):
        request = self.context.get('request')
        size = request.GET.get('size')
        color = request.GET.get('color')
        variants = obj.variants.all()

        if size:
            variants = variants.filter(size__iexact=size)
        if color:
            variants = variants.filter(color__iexact=color)

        return ProductVariantSerializer(variants, many=True).data
