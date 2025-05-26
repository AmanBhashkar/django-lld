from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from store_products import views

urlpatterns = [
    # API schema and docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Test endpoint
    path("hello/", views.hello_world),
    # Product CRUD endpoints
    path("products/", views.get_products, name="get_products"),
    path("products/<int:product_id>/", views.get_product, name="get_product"),
    path("products/add/", views.add_products, name="add_products"),
    path(
        "products/<int:product_id>/update/", views.update_product, name="update_product"
    ),
    path(
        "products/<int:product_id>/delete/", views.delete_product, name="delete_product"
    ),
    # Order CRUD endpoints
    path("orders/", views.get_orders, name="get_orders"),
    path("orders/<int:order_id>/", views.get_order, name="get_order"),
    path("orders/create/", views.create_order, name="create_order"),
    path("orders/<int:order_id>/update/", views.update_order, name="update_order"),
    path("orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    # Payment endpoints (to be implemented)
    path(
        "payments/razorpay/create/",
        views.create_razorpay_order,
        name="create_razorpay_order",
    ),
    path(
        "payments/razorpay/verify/",
        views.verify_razorpay_payment,
        name="verify_razorpay_payment",
    ),
]
