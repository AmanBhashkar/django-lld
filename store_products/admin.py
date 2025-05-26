from django.contrib import admin
import store_products
import store_products.models as models

# Register your models here.


@admin.register(models.Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock_quantity", "is_available", "created_at"]
    list_filter = ["is_available", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["price", "stock_quantity", "is_available"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "total_amount",
        "payment_status",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price_at_time", "get_total_price"]
    list_filter = ["order__status", "created_at"]
    search_fields = ["product__name", "order__user__username"]
