# from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from store_products.models import Products, Order, OrderItem
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import razorpay
from store_products.serializer import (
    ProductSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    OrderItemSerializer,
)
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import logging

# Get loggers
logger = logging.getLogger("store_products")
payment_logger = logging.getLogger("payments")

# Create your views here.


def hello_world(request):
    logger.info("Hello world endpoint accessed")
    with transaction.atomic():
        data = Products.objects.all()
        if data:
            print("before update", data[0].name)
            data[0].name = "ABC"
            data[0].save()
            print("saved successfully")
            data[0].refresh_from_db()
            data = Products.objects.all()
            print("After update", data[0].name)
            print(data[0].name)
    return HttpResponse("Hello World")


# PRODUCT CRUD OPERATIONS


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="name",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter products by name (case-insensitive partial match)",
            required=False,
        ),
        OpenApiParameter(
            name="min_price",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Filter products with price greater than or equal to this value",
            required=False,
        ),
        OpenApiParameter(
            name="max_price",
            type=OpenApiTypes.FLOAT,
            location=OpenApiParameter.QUERY,
            description="Filter products with price less than or equal to this value",
            required=False,
        ),
        OpenApiParameter(
            name="is_available",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter products by availability",
            required=False,
        ),
    ],
    responses={200: ProductSerializer(many=True)},
    description="Get all products with optional filters",
)
@api_view(["GET"])
def get_products(request):
    logger.info(f"Get products endpoint accessed with filters: {request.GET.dict()}")

    queryset = Products.objects.all()

    # Apply filters based on query parameters
    name = request.GET.get("name")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    is_available = request.GET.get("is_available")

    if name:
        queryset = queryset.filter(name__icontains=name)
        logger.info(f"Applied name filter: {name}")

    if min_price:
        try:
            min_price = float(min_price)
            queryset = queryset.filter(price__gte=min_price)
            logger.info(f"Applied min_price filter: {min_price}")
        except ValueError:
            logger.error(f"Invalid min_price value: {min_price}")
            return Response(
                {"error": "Invalid min_price value"}, status=status.HTTP_400_BAD_REQUEST
            )

    if max_price:
        try:
            max_price = float(max_price)
            queryset = queryset.filter(price__lte=max_price)
            logger.info(f"Applied max_price filter: {max_price}")
        except ValueError:
            logger.error(f"Invalid max_price value: {max_price}")
            return Response(
                {"error": "Invalid max_price value"}, status=status.HTTP_400_BAD_REQUEST
            )

    if is_available is not None:
        is_available_bool = is_available.lower() in ["true", "1", "yes"]
        queryset = queryset.filter(is_available=is_available_bool)
        logger.info(f"Applied is_available filter: {is_available_bool}")

    serialized_products = ProductSerializer(queryset, many=True)
    logger.info(f"Returning {len(serialized_products.data)} products")
    return Response(serialized_products.data)


@extend_schema(
    responses={200: ProductSerializer}, description="Get a specific product by ID"
)
@api_view(["GET"])
def get_product(request, product_id):
    logger.info(f"Get product endpoint accessed for product ID: {product_id}")
    try:
        product = get_object_or_404(Products, id=product_id)
        serializer = ProductSerializer(product)
        logger.info(f"Successfully retrieved product: {product.name}")
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise


@extend_schema(
    request=ProductSerializer,
    responses={201: ProductSerializer},
    description="Add a new product",
)
@api_view(["POST"])
def add_products(request):
    logger.info(f"Add product endpoint accessed with data: {request.data}")
    try:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            logger.info(
                f"Successfully created product: {product.name} (ID: {product.id})"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Product creation failed with errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        raise


@extend_schema(
    request=ProductSerializer,
    responses={200: ProductSerializer},
    description="Update a specific product",
)
@api_view(["PUT", "PATCH"])
def update_product(request, product_id):
    logger.info(f"Update product endpoint accessed for product ID: {product_id}")
    try:
        product = get_object_or_404(Products, id=product_id)
        partial = request.method == "PATCH"
        serializer = ProductSerializer(product, data=request.data, partial=partial)
        if serializer.is_valid():
            updated_product = serializer.save()
            logger.info(
                f"Successfully updated product: {updated_product.name} (ID: {product_id})"
            )
            return Response(serializer.data)
        else:
            logger.error(
                f"Product update failed for ID {product_id} with errors: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        raise


@extend_schema(responses={204: None}, description="Delete a specific product")
@api_view(["DELETE"])
def delete_product(request, product_id):
    logger.info(f"Delete product endpoint accessed for product ID: {product_id}")
    try:
        product = get_object_or_404(Products, id=product_id)
        product_name = product.name
        product.delete()
        logger.info(f"Successfully deleted product: {product_name} (ID: {product_id})")
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        raise


# ORDER CRUD OPERATIONS


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter orders by user ID",
            required=False,
        ),
        OpenApiParameter(
            name="status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter orders by status",
            required=False,
        ),
    ],
    responses={200: OrderSerializer(many=True)},
    description="Get all orders with optional filters",
)
@api_view(["GET"])
def get_orders(request):
    logger.info(f"Get orders endpoint accessed with filters: {request.GET.dict()}")

    queryset = Order.objects.all()

    user_id = request.GET.get("user_id")
    order_status = request.GET.get("status")

    if user_id:
        queryset = queryset.filter(user_id=user_id)
        logger.info(f"Applied user_id filter: {user_id}")

    if order_status:
        queryset = queryset.filter(status=order_status)
        logger.info(f"Applied status filter: {order_status}")

    serializer = OrderSerializer(queryset, many=True)
    logger.info(f"Returning {len(serializer.data)} orders")
    return Response(serializer.data)


@extend_schema(
    responses={200: OrderSerializer}, description="Get a specific order by ID"
)
@api_view(["GET"])
def get_order(request, order_id):
    logger.info(f"Get order endpoint accessed for order ID: {order_id}")
    try:
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderSerializer(order)
        logger.info(f"Successfully retrieved order ID: {order_id}")
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {str(e)}")
        raise


@extend_schema(
    request=CreateOrderSerializer,
    responses={201: OrderSerializer},
    description="Create a new order",
)
@api_view(["POST"])
def create_order(request):
    logger.info(f"Create order endpoint accessed with data: {request.data}")
    try:
        serializer = CreateOrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            response_serializer = OrderSerializer(order)
            logger.info(
                f"Successfully created order ID: {order.id} for user: {order.user.username}"
            )
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Order creation failed with errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise


@extend_schema(
    request=OrderSerializer,
    responses={200: OrderSerializer},
    description="Update order status and details",
)
@api_view(["PUT", "PATCH"])
def update_order(request, order_id):
    logger.info(f"Update order endpoint accessed for order ID: {order_id}")
    try:
        order = get_object_or_404(Order, id=order_id)
        partial = request.method == "PATCH"
        serializer = OrderSerializer(order, data=request.data, partial=partial)
        if serializer.is_valid():
            updated_order = serializer.save()
            logger.info(f"Successfully updated order ID: {order_id}")
            return Response(serializer.data)
        else:
            logger.error(
                f"Order update failed for ID {order_id} with errors: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        raise


@extend_schema(responses={204: None}, description="Cancel/Delete an order")
@api_view(["DELETE"])
def cancel_order(request, order_id):
    logger.info(f"Cancel order endpoint accessed for order ID: {order_id}")
    try:
        order = get_object_or_404(Order, id=order_id)

        # Restore stock for cancelled orders
        if order.status != "cancelled":
            for order_item in order.order_items.all():
                product = order_item.product
                product.stock_quantity += order_item.quantity
                product.save()
                logger.info(
                    f"Restored {order_item.quantity} units of {product.name} to stock"
                )

            order.status = "cancelled"
            order.save()
            logger.info(f"Successfully cancelled order ID: {order_id}")
        else:
            logger.info(f"Order ID: {order_id} was already cancelled")

        return Response(
            {"message": "Order cancelled successfully"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {str(e)}")
        raise


# PAYMENT INTEGRATION


@extend_schema(
    request={
        "type": "object",
        "properties": {"order_id": {"type": "integer"}, "amount": {"type": "number"}},
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "razorpay_order_id": {"type": "string"},
                "amount": {"type": "number"},
                "currency": {"type": "string"},
                "key": {"type": "string"},
            },
        }
    },
    description="Create Razorpay order for payment",
)
@api_view(["POST"])
def create_razorpay_order(request):
    payment_logger.info(
        f"Create Razorpay order endpoint accessed with data: {request.data}"
    )
    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order_id = request.data.get("order_id")
        amount = request.data.get("amount")

        if not order_id or not amount:
            payment_logger.error(
                "Missing order_id or amount in Razorpay order creation"
            )
            return Response(
                {"error": "order_id and amount are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the order from database
        order = get_object_or_404(Order, id=order_id)

        # Create Razorpay order
        razorpay_order = client.order.create(
            {
                "amount": int(float(amount) * 100),  # Amount in paise
                "currency": "INR",
                "receipt": f"order_{order_id}",
                "payment_capture": 1,
            }
        )

        # Update order with Razorpay order ID
        order.payment_id = razorpay_order["id"]
        order.save()

        payment_logger.info(
            f"Successfully created Razorpay order {razorpay_order['id']} for order ID: {order_id}"
        )

        return Response(
            {
                "razorpay_order_id": razorpay_order["id"],
                "amount": amount,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID,
            }
        )

    except ImportError:
        payment_logger.error("Razorpay library not installed")
        return Response(
            {"error": "Razorpay library not installed. Run: pip install razorpay"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        payment_logger.error(f"Error creating Razorpay order: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    request={
        "type": "object",
        "properties": {
            "razorpay_payment_id": {"type": "string"},
            "razorpay_order_id": {"type": "string"},
            "razorpay_signature": {"type": "string"},
            "order_id": {"type": "integer"},
        },
    },
    responses={
        200: {
            "type": "object",
            "properties": {"status": {"type": "string"}, "message": {"type": "string"}},
        }
    },
    description="Verify Razorpay payment",
)
@api_view(["POST"])
def verify_razorpay_payment(request):
    payment_logger.info(f"Verify Razorpay payment endpoint accessed")
    try:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_signature = request.data.get("razorpay_signature")
        order_id = request.data.get("order_id")

        payment_logger.info(
            f"Payment verification attempt for order ID: {order_id}, Razorpay order: {razorpay_order_id}"
        )

        if not all(
            [razorpay_payment_id, razorpay_order_id, razorpay_signature, order_id]
        ):
            payment_logger.error("Missing payment details in verification request")
            return Response(
                {"error": "All payment details are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify payment signature
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Payment verified successfully
            order = get_object_or_404(Order, id=order_id)
            order.payment_status = "completed"
            order.status = "confirmed"
            order.save()

            payment_logger.info(
                f"Payment verified successfully for order ID: {order_id}"
            )

            return Response(
                {"status": "success", "message": "Payment verified successfully"}
            )

        except razorpay.errors.SignatureVerificationError:
            payment_logger.error(
                f"Payment verification failed for order ID: {order_id} - Invalid signature"
            )
            return Response(
                {"error": "Payment verification failed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    except ImportError:
        payment_logger.error("Razorpay library not installed")
        return Response(
            {"error": "Razorpay library not installed. Run: pip install razorpay"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        payment_logger.error(f"Error verifying payment: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
