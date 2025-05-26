from rest_framework import serializers
from store_products.models import Products, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_time",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "user_username",
            "status",
            "total_amount",
            "shipping_address",
            "payment_status",
            "payment_id",
            "order_items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CreateOrderSerializer(serializers.ModelSerializer):
    order_items = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField()), write_only=True
    )

    class Meta:
        model = Order
        fields = ["user", "shipping_address", "order_items"]

    def create(self, validated_data):
        order_items_data = validated_data.pop("order_items")
        order = Order.objects.create(**validated_data)

        total_amount = 0
        for item_data in order_items_data:
            product_id = item_data.get("product_id")
            quantity = int(item_data.get("quantity", 1))

            try:
                product = Products.objects.get(id=product_id)
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
                    )

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_time=product.price,
                )

                # Update stock
                product.stock_quantity -= quantity
                product.save()

                total_amount += order_item.get_total_price()

            except Products.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with id {product_id} does not exist"
                )

        order.total_amount = total_amount
        order.save()

        return order
