from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariant, ProductImage
from faker import Faker
import random
import os
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile

fake = Faker()

class Command(BaseCommand):
    help = 'Seed categories, products, images, and variants with Faker'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🔄 Seeding data...'))

        # Categories
        categories = {
            'Clothing': None,
            'Shoes': None,
            'Technology': None,
            'Accessories': None,
            'Bags': None,
            'Kids': None
        }

        for name in categories.keys():
            slug = name.lower()
            categories[name], _ = Category.objects.get_or_create(name=name, slug=slug)

        # Base products
        base_products = [
            {
                "name": "Basic T-Shirt",
                "description": "100% cotton, soft and stylish",
                "price": 15.99,
                "stock": 200,
                "category": categories['Clothing']
            },
            {
                "name": "Laptop Pro 15",
                "description": "High-performance laptop for professionals",
                "price": 1299.99,
                "stock": 50,
                "category": categories['Technology']
            },
            {
                "name": "Running Sneakers",
                "description": "Cushioned sole and breathable upper",
                "price": 89.99,
                "stock": 120,
                "category": categories['Shoes']
            },
            {
                "name": "Smart Watch",
                "description": "Track your fitness and notifications",
                "price": 199.99,
                "stock": 80,
                "category": categories['Accessories']
            },
        ]

        image_path = os.path.join(settings.BASE_DIR, 'default.jpg')

        def attach_image(product):
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    ProductImage.objects.create(
                        product=product,
                        image=File(f, name=f"{product.name.replace(' ', '_').lower()}.jpg")
                    )
            else:
                self.stdout.write(self.style.WARNING(f"⚠️ default.jpg not found — no image added for {product.name}"))

        for prod in base_products:
            product, created = Product.objects.get_or_create(
                name=prod['name'],
                defaults={
                    'description': prod['description'],
                    'price': prod['price'],
                    'stock': prod['stock'],
                    'category': prod['category']
                }
            )
            if created:
                attach_image(product)
                self.stdout.write(f"✅ Added base product: {product.name}")

                # Add variants
                if 'T-Shirt' in product.name:
                    ProductVariant.objects.bulk_create([
                        ProductVariant(product=product, size='S', color='White', stock=50),
                        ProductVariant(product=product, size='M', color='Black', stock=60),
                        ProductVariant(product=product, size='L', color='Blue', stock=40),
                    ])
                elif 'Sneakers' in product.name:
                    ProductVariant.objects.bulk_create([
                        ProductVariant(product=product, size='42', color='Red', stock=30),
                        ProductVariant(product=product, size='43', color='Black', stock=30),
                    ])

        # Random fake products
        for _ in range(10):
            category = random.choice(list(categories.values()))
            product = Product.objects.create(
                name=fake.unique.word().capitalize() + " " + random.choice(['Bag', 'Toy', 'Gadget', 'Shirt']),
                description=fake.sentence(),
                price=round(random.uniform(10, 300), 2),
                stock=random.randint(10, 100),
                category=category
            )
            attach_image(product)
            ProductVariant.objects.create(
                product=product,
                size=random.choice(['S', 'M', 'L', 'XL', '40', '41', '42']),
                color=random.choice(['Red', 'Blue', 'Green', 'Black', 'White']),
                stock=random.randint(5, 50)
            )
            self.stdout.write(f"➕ Added random product: {product.name}")

        self.stdout.write(self.style.SUCCESS('🎉 Seed completed successfully!'))
