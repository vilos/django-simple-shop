from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from catalog.models import Product, TaxClass
from jsonfield import JSONField
from utils import round_cents


class Shop(models.Model):
    """Holds all shop related information.    
    
    Instance variables:
    
    - name
       The name of the shop. This is used for the the title of the HTML pages

    - shop_owner
       The shop owner. This is displayed within several places for instance the
       checkout page

    - from_email
       This e-mail address is used for the from header of all outgoing e-mails

    - notification_emails
       This e-mail addresses are used for incoming notification e-mails, e.g.
       received an order. One e-mail address per line.
    """
    
    name = models.CharField(_(u"Name"), max_length=30)
    shop_owner = models.CharField(_(u"Shop owner"), max_length=100, blank=True)
    from_email = models.EmailField(_(u"From e-mail address"))
    notification_emails  = models.TextField(_(u"Notification email addresses"), blank=True, null=True)
    
    def __unicode__(self):
        return u"%s" % self.name


STATUS_CART = 'cart'
#STATUS_CHECKOUT = 'checkout'
STATUS_CONFIRMED = 'confirmed'
STATUS_COMPLETED = 'completed'

STATUS_CHOICES = (
    (STATUS_CART, _('Cart')),
    #(STATUS_CHECKOUT, _('Checkout')),
    (STATUS_CONFIRMED, _('Confirmed')),
    (STATUS_COMPLETED, _('Completed')),
    )
    
class CartManager(models.Manager):
    def get_query_set(self):
        return super(CartManager, self).get_query_set().filter(status=STATUS_CART)
    
    def from_request(self, request, create=False):
        key = request.session.session_key
        cart = None
        try:
            cart = self.get(session=key)
        except Order.DoesNotExist:
            if create:
                cart = self.create(session=key) 
        return cart      
    
class Order(models.Model):
    '''
    The ``Order`` model represents a customer order or a cart.
    '''
        
    customer = models.ForeignKey(User, blank=True, null=True)
    comments = models.TextField(blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default=STATUS_CART)
    sub_total = models.DecimalField(_("Subtotal"), max_digits=18, decimal_places=10, default=Decimal('0.00'))
    total = models.DecimalField(_("Total"), max_digits=18, decimal_places=10, default=Decimal('0.00'))
    discount = models.DecimalField(_("Discount"), max_digits=18, decimal_places=10, default=Decimal('0.00'))
    tax = models.DecimalField(_("Tax"), max_digits=18, decimal_places=10, default=Decimal('0.00'))
    tax_detail = JSONField(blank=True, null=True)
    
    session = models.CharField(_(u"Session"), blank=True, max_length=100)
    created = models.DateTimeField(_(u"Creation date"), auto_now_add=True)
    modified = models.DateTimeField(_(u"Modification date"), auto_now=True, auto_now_add=True)
    
    carts = CartManager()
    
    def __unicode__(self):
        user = self.customer or _('Anonymous')
        return u'%s: %d items, %s @ %s>' % (user,
                                            self.items_count(),
                                            self.total,
                                            self.created.strftime("%d.%m.%Y %H:%M"))
        
    def editable(self):
        return self.status == STATUS_CART

    def items_count(self):
        return self.items.count()
    
    def items_qty(self):
        """Returns the quantity of all items in the cart.
        """
        qty = 0
        for item in self.items.all():
            qty += item.quantity
        return qty
    
    def add_item(self, product, quantity, absolute=False):
        
        if not self.editable:
            raise ValidationError(_('Cannot modify order once it has been confirmed.'), code='order_sealed')
        try:
            cart_item = self.items.get(product=product)
        except ObjectDoesNotExist:
            cart_item = OrderItem(order=self, product=product, quantity=quantity)
        else:
            if absolute:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
        cart_item.save()
    
    def remove_item(self, item_id):
        cart_item = OrderItem.objects.get(order=self, pk=item_id)
        cart_item.delete()

    def recalculate_totals(self):
        self.sub_total = self.tax = self.discount = Decimal(0)
        tax_detail = {}
        for item in self.items.all():
            self.sub_total += item.line_total_excl_tax
            #self.items_discount += item._line_item_discount or 0
            item_tax = item.line_tax
            tax_detail[item.tax_name] = tax_detail.get(item.tax_name, Decimal(0)) + item_tax
            self.tax += item_tax
            
        self.tax_detail = tax_detail
        self.total = round_cents(self.sub_total - self.discount + self.tax)
        
    def save(self, *args, **kw):
        if self.editable():
            self.recalculate_totals()
        super(Order, self).save(*args, **kw)
        

class OrderItem(models.Model):
    """
    A line item on an order.
    """
    order = models.ForeignKey(Order, verbose_name=_("Order"), related_name="items")
    product = models.ForeignKey(Product, verbose_name=_("Product"))
    quantity = models.DecimalField(_("Quantity"),  max_digits=18,  decimal_places=6)
    unit_price = models.DecimalField(_("Unit price"), max_digits=18, decimal_places=10)
    unit_tax =  models.DecimalField(_("Tax"), max_digits=18, decimal_places=10, blank=True)
    tax_name = models.CharField(_("Tax name"), max_length=100, blank=True)
    tax_included = models.BooleanField(_('tax included'), blank=True)
            
    def save(self, *args, **kwargs):        
        if not self.unit_price or not self.tax_name:
            price = self.product.price
            self.unit_price=price.unit_price
            self.unit_tax=price.unit_tax
            self.tax_name = price.tax_name
            self.tax_included = price.tax_included
        super(OrderItem, self).save(*args, **kwargs)

    @property
    def line_total_excl_tax(self):
        if self.tax_included:
            return self.line_total_incl_tax - self.line_tax
        return self.unit_price * self.quantity
    
    @property
    def line_total_incl_tax(self):
        if self.tax_included:
            return self.unit_price * self.quantity
        return self.line_total_excl_tax + self.line_tax
    
    @property
    def line_total(self):
        if self.tax_included:
            return self.line_total_incl_tax
        else:
            return self.line_total_excl_tax
        
    @property
    def line_tax(self):
        return self.unit_tax * self.quantity
    

