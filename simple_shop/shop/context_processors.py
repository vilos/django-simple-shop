from models import Shop, Order


def get_default_shop():
    """Returns the default shop.
    """
    return Shop.objects.all()[0]
    

def shop_context(request):
    shop = get_default_shop()
    cart = Order.carts.from_request(request, create=False)
    return {
        'shop': shop,
        'cart': cart,
        }
