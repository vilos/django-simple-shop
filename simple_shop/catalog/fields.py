from django.db import models
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from shop.settings import SHOP_CURRENCIES, DEFAULT_CURRENCY

CurrencyField = curry(models.CharField, _('currency'), max_length=3, choices=SHOP_CURRENCIES, default=DEFAULT_CURRENCY)
