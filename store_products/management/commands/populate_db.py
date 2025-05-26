from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store_products.models import Products, Order, OrderItem
from decimal import Decimal
import random
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = "Populate database with dummy data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=10,
            help="Number of users to create (default: 10)",
        )
        parser.add_argument(
            "--products",
            type=int,
            default=50,
            help="Number of products to create (default: 50)",
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=25,
            help="Number of orders to create (default: 25)",
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before populating"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Products.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared."))

        # Create users
        self.stdout.write("Creating users...")
        users = self.create_users(options["users"])
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(users)} users")
        )

        # Create products
        self.stdout.write("Creating products...")
        products = self.create_products(options["products"])
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(products)} products")
        )

        # Create orders
        self.stdout.write("Creating orders...")
        orders = self.create_orders(users, products, options["orders"])
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {len(orders)} orders")
        )

        self.stdout.write(self.style.SUCCESS("Database populated successfully!"))

    def create_users(self, count):
        """Create dummy users"""
        users = []
        first_names = [
            "John",
            "Jane",
            "Mike",
            "Sarah",
            "David",
            "Emily",
            "Chris",
            "Lisa",
            "Robert",
            "Maria",
            "James",
            "Anna",
            "Michael",
            "Emma",
            "William",
        ]
        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
        ]

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}{last_name.lower()}{i+1}"
            email = f"{username}@example.com"

            user = User.objects.create_user(
                username=username,
                email=email,
                password="testpass123",
                first_name=first_name,
                last_name=last_name,
            )
            users.append(user)

        return users

    def create_products(self, count):
        """Create dummy products"""
        products = []

        # Product categories and names
        electronics = [
            "iPhone 15 Pro",
            "Samsung Galaxy S24",
            "MacBook Pro M3",
            "Dell XPS 13",
            "iPad Air",
            "Sony WH-1000XM5",
            "AirPods Pro",
            "Nintendo Switch",
            "PlayStation 5",
            "Xbox Series X",
            "Apple Watch Series 9",
            "Kindle Oasis",
        ]

        clothing = [
            "Nike Air Max 270",
            "Adidas Ultraboost 22",
            "Levi's 501 Jeans",
            "North Face Jacket",
            "Under Armour T-Shirt",
            "Converse Chuck Taylor",
            "Polo Ralph Lauren Shirt",
            "Zara Dress",
            "H&M Sweater",
            "Uniqlo Hoodie",
        ]

        home_garden = [
            "Dyson V15 Vacuum",
            "Instant Pot Duo 7-in-1",
            "KitchenAid Stand Mixer",
            "Philips Air Fryer",
            "Roomba i7+",
            "Nest Thermostat",
            "Ring Doorbell",
            "Shark Navigator Vacuum",
            "Cuisinart Coffee Maker",
            "Vitamix Blender",
        ]

        books = [
            "The Great Gatsby",
            "To Kill a Mockingbird",
            "1984",
            "Pride and Prejudice",
            "The Catcher in the Rye",
            "Lord of the Flies",
            "Harry Potter Series",
            "The Hobbit",
            "Dune",
            "The Alchemist",
            "Think and Grow Rich",
        ]

        sports = [
            "Wilson Tennis Racket",
            "Spalding Basketball",
            "Nike Soccer Ball",
            "Callaway Golf Clubs",
            "Yeti Cooler",
            "Patagonia Backpack",
            "Coleman Tent",
            "REI Sleeping Bag",
            "Hydro Flask Water Bottle",
        ]

        all_products = electronics + clothing + home_garden + books + sports

        categories = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]

        for i in range(count):
            if i < len(all_products):
                name = all_products[i]
            else:
                name = f"Product {i+1}"

            category = random.choice(categories)

            # Generate realistic prices based on category
            if category == "Electronics":
                price = Decimal(random.uniform(99.99, 2999.99))
            elif category == "Clothing":
                price = Decimal(random.uniform(19.99, 299.99))
            elif category == "Home & Garden":
                price = Decimal(random.uniform(29.99, 899.99))
            elif category == "Books":
                price = Decimal(random.uniform(9.99, 49.99))
            else:  # Sports
                price = Decimal(random.uniform(24.99, 599.99))

            # Round to 2 decimal places
            price = price.quantize(Decimal("0.01"))

            description = (
                f"High-quality {name.lower()} in {category.lower()} category. "
                f"Perfect for everyday use with excellent durability and performance."
            )

            product = Products.objects.create(
                name=name,
                description=description,
                price=price,
                stock_quantity=random.randint(5, 100),
                is_available=random.choice([True, True, True, False]),  # 75% available
            )
            products.append(product)

        return products

    def create_orders(self, users, products, count):
        """Create dummy orders with order items"""
        orders = []

        addresses = [
            "123 Main St, New York, NY 10001",
            "456 Oak Ave, Los Angeles, CA 90210",
            "789 Pine Rd, Chicago, IL 60601",
            "321 Elm St, Houston, TX 77001",
            "654 Maple Dr, Phoenix, AZ 85001",
            "987 Cedar Ln, Philadelphia, PA 19101",
            "147 Birch Way, San Antonio, TX 78201",
            "258 Spruce St, San Diego, CA 92101",
            "369 Willow Ave, Dallas, TX 75201",
            "741 Poplar Rd, San Jose, CA 95101",
        ]

        statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        payment_statuses = ["pending", "completed", "failed"]

        for i in range(count):
            user = random.choice(users)
            status = random.choice(statuses)

            # Create order
            order = Order.objects.create(
                user=user,
                status=status,
                shipping_address=random.choice(addresses),
                payment_status=random.choice(payment_statuses),
                total_amount=Decimal("0.00"),  # Will be calculated below
            )

            # Add random created_at date (last 30 days)
            days_ago = random.randint(0, 30)
            order.created_at = timezone.now() - timedelta(days=days_ago)

            # Create order items (1-5 items per order)
            num_items = random.randint(1, 5)
            available_products = [
                p for p in products if p.is_available and p.stock_quantity > 0
            ]

            if not available_products:
                continue

            selected_products = random.sample(
                available_products, min(num_items, len(available_products))
            )

            total_amount = Decimal("0.00")

            for product in selected_products:
                quantity = random.randint(1, min(3, product.stock_quantity))

                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_time=product.price,
                )

                # Update product stock
                product.stock_quantity -= quantity
                product.save()

                # Add to total
                total_amount += order_item.get_total_price()

            # Update order total
            order.total_amount = total_amount
            order.save()

            orders.append(order)

        return orders
