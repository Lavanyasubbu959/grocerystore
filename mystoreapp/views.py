from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
import razorpay
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderCreateForm, SearchForm
from . models import Cart
from . models import  Product, OrderItems, CartItem
from django.contrib.auth.decorators import login_required
from . forms import UserRegistrationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def home(request):
    return render(request, 'home.html')



def product_list(request):
    form = SearchForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        products = products.filter(name__icontains=query)
    
    return render(request, 'product_list.html', {'products': products, 'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product,})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form':form}) 


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('product_list')
            else : 
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def add_to_cart(request, item_type, item_id):
    user_cart, created = CartItem.objects.get_or_create(request)
    if item_type == 'product':
        item = get_object_or_404(Product, id=item_id)
        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=item)


    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = CartItem.objects.get_or_create(user_id=request.user.id)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.total for item in cart_items)
    print("total : ", total)
    return render(request, 'cart_detail.html', {'cart_items' : cart_items, 'total' : total})



@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect(request,'cart_detail')


def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect(request,'cart_detail')


@login_required
def order_create(request):
    #cart = Cart.Objects.grt(id=1)
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart.items.all():
                OrderItems.objects.create(
                    order = order,
                    category = item.category,
                    product = item.product,
                    price = item.product.price,
                    quantity = item.quantity
                )
            cart.items.all().delete()

            client = razorpay.Client(auth=(settings.RAZORPAY_TEST_KEY_ID, settings.RAZORPAY_TEST_KEY_SECRET))
            payment_data = {
                'amount': int(order.total_cost * 100),
                'currency': 'INR',
                'receipt': f'order_{order.id}', 
            }
            print(payment_data)
            payment = client.order.create(data=payment_data)
             
            return render(request, 'order_created.html', {'order': order, 'payment': payment, 'razorpay_key_id': settings.RAZORPAY_TEST_KEY_ID})
    else : 
        form = OrderCreateForm()
    return render(request, 'order_create.html', {'cart': cart, 'form': form})

@login_required
@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        return HttpResponse("Payment Successful")
    return HttpResponse(status=400)




