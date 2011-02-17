from django.conf.urls.defaults import patterns, url
from catalog.models import Product


urlpatterns = patterns( 'shop.views',
    url(r'^cart/$', 'shopping_cart', {}, name='shop_cart'),
    url(r'^cart/add/(?P<slug>[-\w]+)/$', 'add_to_cart', {'queryset': Product.objects.all()}, name='cart_add_product'),
    url(r'^cart/remove/(?P<cart_item_id>\d+)/$', 'remove_from_cart', {}, name='cart_remove_product'),
    url(r'^cart/cancel/$', 'remove_cart', {}, name='cart_remove'),
    url(r'^checkout/$', 'checkout', {}, name='shop_checkout'),
    url(r'^confirmation/$', "confirmation",name="shop_confirmation")
    )
