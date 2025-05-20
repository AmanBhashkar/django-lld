# from django.shortcuts import render
from django.http import HttpResponse
from store_products.models import Products
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response

from store_products.serializer import ProductSerializer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema 

# Create your views here.

def hello_world(request):
    with transaction.atomic():
        data = Products.objects.all()
        if data:
            print("before update" , data[0].name)
            data[0].name = "ABC"
            data[0].save()
            print("saved successfully")
            data[0].refresh_from_db()
            data= Products.objects.all()
            print("After update", data[0].name)
            print(data[0].name)
    return HttpResponse('Hello World')


# @swagger_auto_schema(method='get') 
@api_view(["GET"])
def get_products(requests):
    data = Products.objects.all()
    serialized_products = ProductSerializer(data,many=True)
    return Response(serialized_products.data)

@api_view(["POST"])
def add_products(request):
    print(request)
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  # Save to DB
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)