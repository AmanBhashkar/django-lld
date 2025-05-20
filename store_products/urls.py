from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from store_products import views  # assuming your views are here

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API schema and docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API endpoints
    path('hello/', views.hello_world),
    path('products/', views.get_products),
    path('add_products/', views.add_products),
]
