from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
import razorpay
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderCreateForm, SearchForm, UserRegistrationForm
from .cart import Cart
from . models import Category, Product, OrderItems,  CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout

from mystoreapp import cart

# Create your views here.
def home(request):
    return render(request, 'home.html')


def category_list(request):
    form = SearchForm(request.GET or None)
    categorys = Category.objects.all()

    if form.is_valid():
        query = form.cleaned_data['query']
        categorys = categorys.filter(name__icontains=query)


    return render(request, 'category_list.html', {'categorys': categorys, 'form': form})


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

def add_to_wishlist(request, item_type, item_id):
    # Ensure you handle both item_type and item_id as parameters
    if item_type == 'Product':
        Product = get_object_or_404(Product, pk=item_id)
        # Add product to wishlist logic here
        # Example: request.session.setdefault('wishlist', {})[item_id] = item_type
        wishlist = request.session.get('wishlist', {})
        wishlist[item_id] = item_type
        request.session['wishlist'] = wishlist
    # Handle other item types if necessary
    return redirect('wishlist')  # Redirect to the wishlist page

def remove_from_wishlist(request, item_type, item_id):
    wishlist = request.session.get('wishlist', {})
    if str(item_id) in wishlist and wishlist[str(item_id)] == item_type:
        del wishlist[str(item_id)]
        request.session['wishlist'] = wishlist
    return redirect('wishlist')



def wishlist(request):
    wishlist = request.session.get('wishlist', {})
    product_ids = [id for id, type in wishlist.items() if type == 'product']

    wishlist_products = Product.objects.filter(id__in=product_ids)

    return render(request, 'wishlist.html', {'wishlist_products': wishlist_products})

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart_detail.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('cart_detail')



def increase_quantity(request, item_id):
    # Fetch the CartItem object, not the Cart object
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

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)  # Adjust according to your logic
    total = sum(item.quantity * item.product.price for item in cart_items)  # Adjust according to your logic
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})



@login_required
def order_create(request):
    cart = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart.items.all():
                OrderItems.objects.create(
                    order = order,
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




