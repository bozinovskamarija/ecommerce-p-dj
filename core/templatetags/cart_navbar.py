from django import template
from core.models import Order

register = template.Library() #za registrovanje template tag-a

#funkcija sa imenom template tag-a
@register.filter
def cart_item_count(user):
    #ako user nije ulogovan necemo da se ista prikazuje u kartici
    if user.is_authenticated:
        #ordered=false - ne zelimo da se prikazuju njihove prethodne porudžbine
        q = Order.objects.filter(user=user, is_ordered=False)
        if q.exists():
            #uzimanje jedine narudžbine iz tog upita (query set) i broja artikala
            return q[0].items.count()
    #ako user nije autentifikovan
    return 0 

