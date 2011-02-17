from django.http import Http404
from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.views.decorators.cache import never_cache
from django.template import RequestContext
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _
from customers.forms import CustomerForm, AddressForm
from customers.models import Customer, Address
from models import Order, OrderItem, STATUS_CONFIRMED


def lookup_object(queryset, object_id=None, slug=None, slug_field=None):
    if object_id is not None:
        obj = queryset.get(pk=object_id)
    elif slug and slug_field:
        kwargs = {slug_field: slug}
        obj = queryset.get(**kwargs)
    else:
        raise Http404
    return obj

def get_shopping_cart(request):
    return Order.carts.from_request(request, create=True)

@never_cache
def shopping_cart(request, template_name='shop/cart.html'):
    '''
    This view allows a customer to see what products are currently in
    their shopping cart.
    '''
    cart = get_shopping_cart(request)
    
    OrderItemFormset = inlineformset_factory(
        Order,
        OrderItem,
        extra=0,
        fields=('quantity',),
        )
    
    if request.method == 'POST':
        formset = OrderItemFormset(request.POST, instance=cart)

        if formset.is_valid():
            changed = False
            for form in formset.forms:
                if formset.can_delete and formset._should_delete_form(form):
                    cart.remove_item(form.instance.id)
                    changed = True
                elif form.has_changed():
                    cart.add_item(form.instance.product,
                        quantity=form.cleaned_data['quantity'],
                        absolute=True)
                    changed = True

            if changed:
                cart.save()
                messages.success(request, _('The cart has been updated.'))

            if 'checkout' in request.POST:
                return redirect('shop_checkout')
            return redirect('shop_cart')
    else:
        formset = OrderItemFormset(instance=cart)
    
    ctx = {
        'cart': cart,
        'cartformset': formset
        }
    return render_to_response(template_name, ctx,
                              context_instance=RequestContext(request))

@never_cache
def add_to_cart(request, queryset, object_id=None, slug=None,
                slug_field='slug', template_name='shop/added_to_cart.html'):
    '''
    This view allows a customer to add a product to their shopping
    cart. A single GET parameter can be included to specify the
    quantity of the product to add.
    '''
    obj = lookup_object(queryset, object_id, slug, slug_field)
    quantity = request.REQUEST.get('quantity', 1)
    cart = get_shopping_cart(request)
    cart.add_item(obj, quantity)
    cart.save()
    return redirect('shop_cart')
    #return redirect(obj)

@never_cache
def remove_from_cart(request, cart_item_id):
    '''
    This view allows a customer to remove a product from their shopping
    cart. It simply removes the entire product from the cart, without
    regard to quantities.
    '''
    cart = get_shopping_cart(request)
    cart.remove_item(cart_item_id)
    cart.save()
    return redirect('shop_cart')

@never_cache
def remove_cart(request):
    '''
    '''
    cart = get_shopping_cart(request)
    cart.delete()
    return redirect('shop_cart')

def get_customer(request):
    return Customer.objects.from_request(request)

@never_cache
def checkout(request, template_name="shop/checkout.html"):
    cart = get_shopping_cart(request)
    if cart.items_count() == 0:
        return redirect('shop_cart')
    customer = get_customer(request)

    c_form = CustomerForm(prefix='customer', instance=customer)
    s_form = AddressForm(prefix='shipping', instance=getattr(customer, 'shipping_address', None))
    b_form = AddressForm(prefix='billing', instance=getattr(customer, 'billing_address', None))
    
    if request.method == 'POST':
        c_form = CustomerForm(request.POST, prefix='customer', instance=customer)
        commit = True
        if c_form.is_valid():
            customer = c_form.save(commit=False)
            
            s_form = AddressForm(request.POST, prefix='shipping', instance=customer.shipping_address)
            if s_form.is_valid():
                customer.shipping_address = s_form.save(commit=False)
                if customer.same_address:
                    customer.billing_address = customer.shipping_address
                else:
                    b_form = AddressForm(request.POST, prefix='billing', instance=customer.billing_address)
                    if b_form.is_valid():
                        customer.billing_address = b_form.save(commit=False)
                    else:
                        commit = False
            else:
                commit = False
            if commit:
                customer.save()

                if not cart.customer:
                    cart.customer = customer
                cart.status = STATUS_CONFIRMED
                cart.save()
                
                return redirect('shop_confirmation')
    
    return render_to_response(template_name, {
                                'cart': cart,
                                'customerform': c_form,
                                'shippingform': s_form,
                                'billingform': b_form,
                                }, context_instance=RequestContext(request))

@never_cache
def confirmation(request, template_name="shop/confirmation.html"):
    #cart = get_shopping_cart(request)
    #if not cart:
    #    return redirect('shop_cart')
    customer = get_customer(request)
    return render_to_response(template_name, {
                                #'cart': cart,
                                'customer': customer,
                                }, context_instance=RequestContext(request))

