from django.shortcuts import render, redirect
from django.views import View
from . models import Product, Customer, Cart, OrderPlaced
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.
@method_decorator(login_required, name = 'dispatch')
class ProductView(View):
     def get(self, request):
          totalitem = 0
          gentspants = Product.objects.filter(category = 'GP')
          borkhas = Product.objects.filter(category = 'BK')
          babyfashions = Product.objects.filter(category = 'BF')
          lehenga = Product.objects.filter(category = 'L')
          if request.user.is_authenticated:
               totalitem = len(Cart.objects.filter(user=request.user))
               
          return render(request, 'Shop/home.html', {'gentspants':gentspants,'borkhas':borkhas,'babyfashions':babyfashions,'lehenga':lehenga,'totalitem':totalitem })

class ProductDetailView(View):
     def get(self,request, pk):
          product = Product.objects.get(pk=pk)
          item_already_in_cart = False
          if request.user.is_authenticated:
               item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
          return render(request, 'Shop/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart})


@login_required
def add_to_cart(request):
     user = request.user
     product_id = request.GET.get('prod_id')
     product = Product.objects.get(id = product_id)
     Cart(user = user, product=product).save()
     return redirect('/cart')

@login_required
def show_cart(request):
     if request.user.is_authenticated:
          user = request.user
          cart = Cart.objects.filter(user=user)
          amount = 00.0
          shipping_amount = 100.0
          total_amount = 00.0
          totalitem = 0
          if request.user.is_authenticated:
               totalitem = len(Cart.objects.filter(user=request.user))
               
          # using list comprehension
          cart_product = [p for p in Cart.objects.all() if p.user==user]
          if cart_product:
               for p in cart_product:
                    tempamount = (p.quantity * p.product.discounted_price)
                    amount += tempamount
                    totalamount = amount + shipping_amount
                        
               return render(request, 'Shop/addtocart.html', {'carts':cart, 'amount':amount, 'totalamount':totalamount, 'totalitem':totalitem})
          else:
               return render(request, 'Shop/emptycart.html')

def buy_now(request):
 return render(request, 'Shop/buynow.html')

class ProfileView (View):
     def get(self, request):
          form = CustomerProfileForm()     
          return render(request, 'Shop/profile.html', {'form':form})
     
     def post(self, request):
          form = CustomerProfileForm(request.POST)
          if form.is_valid():
               usr = request.user
               name = form.cleaned_data['name']
               division = form.cleaned_data['division']
               district = form.cleaned_data['district']
               thana = form.cleaned_data['thana']
               villorroad = form.cleaned_data['villorroad']
               zipcode = form.cleaned_data['zipcode']
               reg = Customer(user=usr, name=name, division=division, district=district, thana=thana, villorroad=villorroad, zipcode=zipcode)
               reg.save()
               messages.success(request, 'Congratulations! Profile Updated Successfully')
          return render (request, 'Shop/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
     add = Customer.objects.filter(user= request.user)
     return render(request, 'Shop/address.html', {'add':add, 'active':'btn-warning'})

@login_required
def orders(request):
     op = OrderPlaced.objects.filter(user=request.user)
     return render(request, 'Shop/orders.html', {'order_placed':op})

def change_password(request):
 return render(request, 'Shop/changepassword.html')

def lehenga(request, data = None):
     if data == None:
          lehengas = Product.objects.filter(category='L')
     elif data == 'lubnan' or data == 'infinity':
          lehengas = Product.objects.filter(category = 'L').filter(brand=data)
     elif data == 'below':
          lehengas = Product.objects.filter(category='L').filter(discounted_price__lt = 10000)
     elif data == 'above':
          lehengas = Product.objects.filter(category = 'L').filter(discounted_price__gt = 10000)
     return render(request, 'Shop/lehenga.html', {'lehengas': lehengas})

# def login(request):
#      return render(request, 'Shop/login.html')

class CustomerRegistrationView(View):
     def get(self, request):
          form = CustomerRegistrationForm()
          return render(request, 'Shop/customerregistration.html',{'form':form})
     def post(self, request):
          form = CustomerRegistrationForm(request.POST)
          if form.is_valid():
               messages.success(request, 'Congratulations, registration done')
               form.save()
          return render(request, 'Shop/customerregistration.html',{'form':form})
# checkout 
@login_required
def checkout(request):
     user = request.user
     add = Customer.objects.filter(user=user)
     cart_items = Cart.objects.filter(user=user)
     amount = 00.0
     shipping_amount = 100.0
     total_amount = 00.0
     # using list comprehension
     cart_product = [p for p in Cart.objects.all() if p.user==request.user]
     if cart_product:
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               totalamount = amount + shipping_amount
          
     return render(request, 'Shop/checkout.html', {'add':add, 'totalamount':totalamount, 'cart_items':cart_items})

# plus cart icon
def plus_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
          c.quantity += 1
          c.save()
          amount = 00.0
          shipping_amount = 100.0
          total_amount = 00.0
          cart_product = [p for p in Cart.objects.all() if p.user==request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               totalamount = amount + shipping_amount
          
          # returning data as Json Response
          data = {
               'quantity': c.quantity,
               'amount':amount,
               'totalamount': totalamount,
               }     
          return JsonResponse(data)
     
# minus cart Icon
def minus_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
          c.quantity -= 1
          c.save()
          amount = 00.0
          shipping_amount = 100.0
          total_amount = 00.0
          cart_product = [p for p in Cart.objects.all() if p.user==request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               totalamount = amount + shipping_amount
          
          # returning data as Json Response
          data = {
               'quantity': c.quantity,
               'amount':amount,
               'totalamount': totalamount,
               }     
          return JsonResponse(data)
     
# Remove cart
def remove_cart(request):
     if request.method == 'GET':
          prod_id = request.GET['prod_id']
          c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
          c.delete()
          amount = 00.0
          shipping_amount = 100.0
          total_amount = 00.0
          cart_product = [p for p in Cart.objects.all() if p.user==request.user]
          for p in cart_product:
               tempamount = (p.quantity * p.product.discounted_price)
               amount += tempamount
               totalamount = amount + shipping_amount
          
          # returning data as Json Response
          data = {
               'amount':amount,
               'totalamount': totalamount,
               }     
          return JsonResponse(data)

def payment_done(request):
     user = request.user
     custid = request.GET.get('custid')
     customer = Customer.objects.get(id = custid)
     cart = Cart.objects.filter(user=user)
     for c in cart:
          OrderPlaced(user = user, customer = customer, product = c.product, quantity=c.quantity).save()
          c.delete()
     return redirect('orders')
          
def search(request):
     if request.method == 'GET':
          query = request.GET.get('quary')
          if query:
               product = Product.objects.filter(title__icontains = query)
               return render(request, 'Shop/search.html', {'product':product})
          else:
               return render(request, 'Shop/search.html', {'product':product})