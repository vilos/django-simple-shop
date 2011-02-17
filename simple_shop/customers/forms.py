from django import forms
from models import Customer, Address
#from shop.templatetags.formutils import FormOptions

class CustomerForm(forms.ModelForm):
    """ Form to enter customer's data """
    
    #def clean(self):
    #    return super(CustomerForm, self).clean()
    
    class Meta:
        model = Customer
        fields = ('firstname', 'lastname', 'email', 'phone', 'same_address')
    
    
class AddressForm(forms.ModelForm):
    """Form to edit addresses.
    """
    
#    def __init__(self, data=None, customer=None, *args, **kw):
#        self.customer = customer
#        super(AddressForm, self).__init__(data, *args, **kw)
#
#    def save(self, commit=True):
#        obj = super(AddressForm, self).save(commit=commit)
#        if self.customer:
#            obj.customer = self.customer
#        if commit:
#            obj.save()
#        return obj
    
    class Meta:
        model = Address
        # TODO: make configurable
        exclude = ("customer", "country")
