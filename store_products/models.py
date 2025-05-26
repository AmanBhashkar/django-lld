from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AuditData(models.Model):
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Products(AuditData):
    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField()
    price: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    is_available: models.BooleanField = models.BooleanField(default=True)
    stock_quantity: models.IntegerField = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Products"


class Order(AuditData):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user: models.ForeignKey[User, User] = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    total_amount: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    shipping_address: models.TextField = models.TextField()
    payment_status: models.CharField = models.CharField(max_length=20, default="pending")
    payment_id: models.CharField = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]


class OrderItem(AuditData):
    """Many-to-Many relationship between Products and Orders"""

    order: models.ForeignKey[Order, Order] = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product: models.ForeignKey[Products, Products] = models.ForeignKey(
        Products, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity: models.PositiveIntegerField = models.PositiveIntegerField(default=1)
    price_at_time: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # Price when ordered

    def __str__(self):
        return f"{self.product.name} x {self.quantity} in Order #{self.order.id}"

    def get_total_price(self):
        return self.quantity * self.price_at_time

    class Meta:
        unique_together = ["order", "product"]


# Products.objects.all()
