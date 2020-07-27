from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    # ('P', 'PayPal')
)
class CheckoutForm(forms.Form):
    first_name_a = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Marija'}))
    last_name_a = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Bozinovska'}))
    street_address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '12 Manhattan Street'}))
    apartment_number = forms.CharField (widget=forms.TextInput(attrs={'placeholder': 'Apartment No.'}))
    country = CountryField(blank_label='(select country)').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    zip_code = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    shipping_address_same_as_billing_address = forms.BooleanField(required=False) 
    save_info_for_the_next_time = forms.BooleanField(required=False) 
    payment_options = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class DiscountCodeForm(forms.Form):
    discount_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Discount code', 'aria-label':'Recipient\'s username','aria-describedby':'basic-addon2'}))

