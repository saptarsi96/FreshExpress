from django.http.response import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from cart.cart import Cart
from store.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from cart.forms import CartForm
# Create your views here.


def displayitems(request):
    result = Product.objects.all()
    print(result)
    return render(request, 'index5.html', {"items": result})


def order1(request):
    return HttpResponse("you are too good")


def order(request):
    orderlist = {}
    items1 = ['1kg arhard daal', 'Surf-Excel', 'Ariel',
              'Toothpaste', 'Mouth-wash', 'Axe perfume', '5 Kg flour']
    items2 = ['2kg arhard daal', 'Surf-Excel', 'Ariel',
              'Toothpaste', 'Mouth-wash', 'Axe perfume', '5 Kg flour']
    items3 = ['3kg arhard daal', 'Surf-Excel', 'Ariel',
              'Toothpaste', 'Mouth-wash', 'Axe perfume', '5 Kg flour']
    items4 = ['4kg arhard daal', 'Surf-Excel', 'Ariel',
              'Toothpaste', 'Mouth-wash', 'Axe perfume', '5 Kg flour']
    items5 = ['5kg arhard daal', 'Ariel', 'Toothpaste',
              'Mouth-wash', 'Axe perfume', '5 Kg flour']
    orderlist["first"] = items1
    orderlist["second"] = items2
    orderlist["third"] = items3
    orderlist["Fourth"] = items4
    orderlist["fifth"] = items5

    context = {'li': orderlist}
    return render(request, 'index4.html', context)


@login_required
@require_POST
def add_to_cart(request):
    cart = Cart(request)
    form = CartForm(request.POST)
    if form.is_valid():
        product_id = form.cleaned_data['product_id']
        quantity = form.cleaned_data['quantity']
        product = get_object_or_404(Product, id=product_id, availibility=True)
        cart.add(product_id, product.price, quantity)
        messages.success(request, f'{product.name} added to cart.')
    return redirect('cart:cart_details')


@login_required
def cart_details(request):
    cart = Cart(request)
    products = Product.objects.filter(pk__in=cart.cart.keys())
    productkeys = list(cart.cart.keys())
    productlist = ' '.join(map(str, productkeys))

    def map_function(p):
        pid = str(p.id)
        q = cart.cart[pid]['quantity']
        return {'product': p, 'quantity': q, 'total': p.price*q, 'form': CartForm(initial={'quantity': q, 'product_id': pid})}

    cart_items = map(map_function, products)
    return render(request, 'cart/cart_details.html', {'cart_items': cart_items, 'total': cart.get_total_price(), 'productlist': productlist})


@login_required
def remove_from_cart(request, id):
    cart = Cart(request)
    cart.remove(str(id))
    return redirect('cart:cart_details')


@login_required
def clear_cart(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_details')
