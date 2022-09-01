from enum import Flag
from itertools import product
from venv import create
from django.shortcuts import render
from django.http import JsonResponse
import json
from .models import *
from .utils import cookieCart, cartData, gustOrder
import datetime

def store(request):

    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {
        'products': products,
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)

def cart(request):

    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {
        'items': items,
        'order': order,
        'cartItems': cartItems,
    }
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    print(data)
    productId = data['productId']
    action = data['action']

    customer = request.user.customer
    print(customer)
    product = Product.objects.get(id=productId)
    order, create = Order.objects.get_or_create(customer=customer, complite=False)

    orderItem, create = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Response data', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, create = Order.objects.get_or_create(customer=customer, complite=False)
        print('if',order.id)
    
    else:
        customer, order =  gustOrder(request, data)
        print('else',order.id)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complite = True
    print('before seve', order.customer, order.transaction_id, order.date_ordered, order.complite)
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('payment complete', safe=False)