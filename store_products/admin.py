from django.contrib import admin
import store_products
import store_products.models as models

# Register your models here.

admin.site.register(models.Products)