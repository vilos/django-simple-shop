from metaforms import ParentsIncludedModelFormMixin, ParentsIncludedModelFormMetaclass
from customers.forms import CustomerForm, AddressForm


class CheckoutForm(ParentsIncludedModelFormMixin, CustomerForm, AddressForm):
    error_css_class = 'error'
    required_css_class = 'required'
    fieldset = CustomerForm.fieldset + AddressForm.fieldset
    
    __metaclass__ = ParentsIncludedModelFormMetaclass