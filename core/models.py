from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField


CATEGORY_CHOICES = (
    ('C','Classy wear'),
    ('CW','Casual wear'),
    ('O','Sportswear')

)

LABEL_CHOICES = (
    ('P','primary'),
    ('D','danger')
)

class Item(models.Model):
    title = models.CharField(max_length=50)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True)
    slug = models.SlugField()
    description = models.TextField()
    image_home = models.ImageField(null=True)
    image1_product = models.ImageField(null=True)
    image2_product = models.ImageField(null=True)
    image3_product = models.ImageField(null=True)
    image4_product = models.ImageField(null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product-page", kwargs={'slug':self.slug})

    def get_add_to_cart_url(self):
         return reverse("core:add-to-cart", kwargs={'slug':self.slug})

    def get_remove_from_cart_url(self):
         return reverse("core:remove-from-cart", kwargs={'slug':self.slug}) 

    class Meta:
        ordering = ['image_home'] 

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_total_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)

    start_date=models.DateTimeField(auto_now_add=True)
    order_date=models.DateTimeField()

    is_ordered=models.BooleanField(default=False)

    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payments', on_delete=models.SET_NULL, blank=True, null=True)

    discount_code = models.ForeignKey('DiscountCode', on_delete=models.SET_NULL, blank=True, null=True)


    def __str__(self):
         return self.user.username

    def get_total(self):
        total=0
        for order_item in self.items.all():
           total+= order_item.get_total_price()
        if(self.discount_code):
           total -= self.discount_code.amount_discount_code
        return total

class DiscountCode(models.Model):
    discount_code = models.CharField(max_length=15)
    amount_discount_code = models.FloatField() 

    def __str__(self):
        return self.discount_code

class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name_a = models.CharField(max_length=100)
    last_name_a = models.CharField(max_length=100)
    street_address=models.CharField(max_length=100)
    apartment_number=models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip_code=models.CharField(max_length=100)
        
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Billing Address"

class Payments(models.Model):
    stripe_charge_id=models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount=models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
          return str(self.user)

    class Meta:
        verbose_name_plural = "Payments"


