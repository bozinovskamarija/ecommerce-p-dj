from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CheckoutForm, DiscountCodeForm
from .models import Item, Order, OrderItem, BillingAddress, Payments, DiscountCode

from django.core.mail import send_mail
from django.db.models import Q

class SearchResultsView(ListView):
    models=Item
    template_name='search_results.html'

    def get_queryset(self): # new
        query = self.request.GET.get('q')
        object_list = Item.objects.filter(
            Q(title__icontains=query)
        )
        return object_list


import stripe
stripe.api_key = settings.SECRET_KEY

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, is_ordered=False)
        context = { 'order':order }    
        #e-mail
        order.user  = self.request.user
        send_mail( 
        'SHYNESS - Order', 
        'Thank you for your order! If you are seeing this page, you will get another e-mail with arrival day of your ordered items. Thank you for your trust! If you have any troubles contact us via marijabozinovska545@gmail.com',
        'marijabozinovska545@gmail.com', 
        [ order.user.email ]
        ) 

        return render(self.request,"payment-page.html", context)

    def post(self, *args, **kwargs):
        order=Order.objects.get(user=self.request.user, is_ordered=False)
        token=self.request.POST.get('stripeToken')  
        amount=int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(amount=amount, currency="eur", source=token )
            payment = Payments()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(is_ordered=True)
            for item in order_items:
                item.save()

            order.is_ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "You made successful order! Check your e-mail for confirmation.")
                 
            return redirect("/")

        except stripe.error.CardError as e:
             # Since it's a decline, stripe.error.CardError will be caught
             body = e.json_body
             err = body.get('error', {})
             messages.warning(self.request,f"{err.get('message')}")
             return redirect("/")
        except stripe.error.RateLimitError as e:
             # Too many requests made to the API too quickly
             messages.warning(self.request,f"{err.get('RateLimitError - Too many requests made to the API too quickly ')}")
             return redirect("/")
        except stripe.error.InvalidRequestError as e:
             # Invalid parameters were supplied to Stripe's API
             messages.warning(self.request,"Invalid parameters")
             return redirect("/")
        except stripe.error.AuthenticationError as e:
             # Authentication with Stripe's API failed
             messages.warning(self.request,"Authentication error")
             return redirect("/")
        except stripe.error.APIConnectionError as e:
             # Network communication with Stripe failed
             messages.warning(self.request,"APIConnectionError- Network communication with Stripe failed")
             return redirect("/")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send yourself an email
             messages.warning(self.request,"StripeError occurred")
             return redirect("/")
        except Exception as e:
             # Something else happened, completely unrelated to Stripe
             messages.warning(self.request,"Serious error occurred, we have been notified. You are not charged.")
             return redirect("/")

class CheckoutView(View):
    def get (self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            form = CheckoutForm ()
            context = { 'form': form, 'discountcodeform': DiscountCodeForm(), 'order': order  }
            return render(self.request,"checkout-page.html", context) 

        except ObjectDoesNotExists:
            message.info(self.request,"You don't have an active order, so u can't use discount code.")
            return redirect("core:checkout-page")


    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False) 
            if form.is_valid():  
                first_name_a = form.cleaned_data.get('first_name_a')
                last_name_a = form.cleaned_data.get('last_name_a')
                street_address = form.cleaned_data.get('street_address')
                apartment_number = form.cleaned_data.get('apartment_number')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')    
                payment_options = form.cleaned_data.get('payment_options')
                billing_address = BillingAddress( user = self.request.user, first_name_a=first_name_a, last_name_a=last_name_a, street_address=street_address, apartment_number=apartment_number, country = country, zip_code=zip_code)
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_options == 'S':
                    messages.success(self.request, "Successfull checkout! Please enter card details.")
                    return redirect('core:payment-page', payment_options='stripe')
                elif payment_options == 'P':
                    return redirect('core:payment-page', payment_options='paypal')
                else:
                    messages.warning(self.request, "Payment option is invalid. Failed checkout.")
                    return redirect('core:checkout-page')

        except ObjectDoesNotExist: 
            messages.error(self.request, "There is not active order")
            return redirect("core:order-summary")

def products(request):
    context = {
        'items': Item.objects.all().order_by('label')
    }
    return render(request, "product-page.html", context)

class HomeView(ListView):
  model = Item 
  paginate_by = 8
  template_name = "home-page.html"

class SportswearView(ListView):
  model = Item
  Item.category=='O'
  paginate_by = 10
  template_name = "sportswear.html"

class CasualswearView(ListView):
  model = Item
  Item.category=='CW'
  paginate_by = 10
  template_name = "casual_wear.html"

class ClassywearView(ListView):
  model = Item
  Item.category=='C'
  paginate_by = 10
  template_name = "classy_wear.html"


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False) 
            context = { 'object': order }

            return render(self.request, 'order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "There is not an active order")
            return redirect("/")

class ItemDetailView(DetailView):
    model = Item
    template_name = "product-page.html"

@login_required
def add_to_cart(request, slug):
    item =  get_object_or_404(Item, slug=slug )
    order_item, created = OrderItem.objects.get_or_create( item=item, user=request.user,is_ordered=False )
    order_q = Order.objects.filter(user=request.user, is_ordered=False)
    if(order_q.exists()):
        order=order_q[0]
        if order.items.filter(item__slug=item.slug).exists(): 
            order_item.quantity += 1 
            order_item.save()
            messages.info(request, "Item quantity is updated!")
            return redirect("core:order-summary")
        else: 
            order.items.add(order_item)         
            messages.info(request, "Item added to your cart!")
            return redirect("core:order-summary")
    else: 
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, order_date=order_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart!")
        return redirect("core:order-summary")

@login_required
def remove_from_cart(request, slug):
    item =  get_object_or_404(Item, slug=slug)
    order_q = Order.objects.filter(user=request.user, is_ordered=False)
    if order_q.exists():
        order=order_q[0]
        if order.items.filter(item__slug=item.slug).exists():     
            order_item =  OrderItem.objects.filter( item=item, user=request.user,is_ordered=False )[0]     
            order.items.remove(order_item)
            messages.info(request, "Item is removed from your cart!")
            return redirect("core:order-summary")
        else: 
            messages.info(request, "You are trying to remove item that is not in your cart!")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You don't have an active order, so u can't remove item from the cart!")
        return redirect("core:product-page", slug=slug)

@login_required
def remove_one_item_from_cart(request, slug):
    item =  get_object_or_404(Item, slug=slug)
    order_q = Order.objects.filter(user=request.user, is_ordered=False)
    if order_q.exists():
        order=order_q[0]
        if order.items.filter(item__slug=item.slug).exists():     
            order_item =  OrderItem.objects.filter( item=item, user=request.user,is_ordered=False )[0]   
            if order_item.quantity > 1:  
               order_item.quantity -= 1 
               order_item.save()
            else: order.items.remove(order_item) 
            messages.info(request, "Item quantity is deacreased!")
            return redirect("core:order-summary")
        else: 
            messages.info(request, "You are trying to remove item that is not in your cart!")
            return redirect("core:product-page", slug=slug)
    else:
        messages.info(request, "You don't have an active order, so u can't remove item from the cart!")
        return redirect("core:product-page", slug=slug)

def get_discount_code(request, discount_code):
    try:
        discount_code = DiscountCode.objects.get(discount_code=discount_code)
        return discount_code

    except ObjectDoesNotExists:
        message.info(request,"You entered non existing coupun. Please try again.")
        return redirect("core:checkout-page")

def add_discount_code(request):
    if request.method == "POST":
        form = DiscountCodeForm(request.POST or None)
        if form.is_valid():
            try:
                discount_code = form.cleaned_data.get('discount_code')
                #check if there is an order
                order = Order.objects.get(user=request.user, is_ordered=False)
                #assign the coupon to the order
                order.discount_code  = get_discount_code(request, discount_code)
                order.save()
                messages.success(request,"Successfully used discount code.")
                return redirect("core:checkout-page")

            except ObjectDoesNotExist:
                messages.info(request,"You don't have an active order, so u can't use discount code.")
                return redirect("core:checkout-page")

    return None





