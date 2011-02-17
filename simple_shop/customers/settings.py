# coding: utf-8
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

SHOP_COUNTRIES = getattr(settings, 'SHOP_COUNTRIES',(
        ('CZ', _('Czech Republic')),
        ('SK', _('Slovakia')),
    )
)

DEFAULT_COUNTRY = getattr(settings, 'DEFAULT_COUNTRY', 'CZ')