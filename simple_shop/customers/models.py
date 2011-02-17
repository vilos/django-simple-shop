from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
import settings  

class CustomerManager(models.Manager):
    def from_request(self, request, create=False):
        session_key = request.session.session_key
        user = request.user
        
        customer = None
        
        if user.is_authenticated():
            try:
                customer = self.get(user = user)
            except ObjectDoesNotExist:
                pass
        else:
            try:
                customer = self.get(session = session_key)
            except ObjectDoesNotExist:
                pass
    
        if customer is None and create == True:
            customer = Customer(session = request.session.session_key)
            if request.user.is_authenticated():
                customer.user = request.user

            customer.save()
        return customer


class Customer(models.Model):
    '''
    Customer model, optionally connected to the User model for authentication 
    '''

    user = models.ForeignKey(User, blank=True, null=True)
    session = models.CharField(blank=True, max_length=100)
    
    firstname = models.CharField(_(u"Firstname"), max_length=50)
    lastname = models.CharField(_(u"Lastname"), max_length=50)
    email = models.EmailField(_(u"E-Mail"), max_length=50, unique=True)
    phone = models.CharField(_(u"Phone"), max_length=20)
    same_address = models.BooleanField(_('Shipping same as billing?'), default=True)
    shipping_address = models.ForeignKey("Address", verbose_name=_(u"Shipping address"), blank=True, null=True, related_name='ship_to')
    billing_address = models.ForeignKey("Address", verbose_name=_(u"Billing address"), blank=True, null=True, related_name='bill_to')

    objects = CustomerManager()
    
    def __unicode__(self):
        if self.firstname:
            return u"%s %s" % (self.firstname, self.lastname)
        elif self.session:
            return u"%s" % self.session
        return u"Unknown"
        
    
class Address(models.Model):
    """An address which can be used as shipping and/or invoice address.
    """
    #customer = models.ForeignKey(Customer, verbose_name=_(u"Customer"), blank=True, null=True, related_name="addresses")
    addressee = models.CharField(_(u"Addressee"), max_length=80)
    street = models.CharField(_(u"Street"), max_length=100)
    zip_code = models.CharField(_(u"Zip code"), max_length=10)
    city = models.CharField(_(u"City"), max_length=50)
    #state = models.CharField(_("State"), max_length=50, blank=True)
    country =  models.CharField(_(u"Country"), max_length=2, choices=settings.SHOP_COUNTRIES, default=settings.DEFAULT_COUNTRY)
    #models.ForeignKey(Country, verbose_name=_(u"Country"), blank=True, null=True)

    def __unicode__(self):
        return "%s, %s" % (self.city, self.street)
    
    class Meta:
        verbose_name_plural = "addresses"
        ordering = ['country', 'addressee']
    