# coding: utf-8
from django.conf import settings

# Are prices shown with tax included or not?
SHOP_PRICE_INCLUDES_TAX = getattr(settings, 'SHOP_PRICE_INCLUDES_TAX', True)

SHOP_CURRENCIES = getattr(settings, 'SHOP_CURRENCIES', (
    ('CZK', 'CZK'),
    ('EUR', 'EUR'),
    ('USD', 'USD'),
    ))

CURRENCY_FORMATS = getattr(settings, 'CURRENCY_FORMATS', {
        'USD' : {'symbol': u'$', 'positive' : u"$%(val)0.2f", 'negative': u"-$%(val)0.2f", 'decimal' : '.', 'thousands_sep': ','},
        'GBP' : {'symbol': u'£', 'positive' : u"£%(val)0.2f", 'negative': u"-£%(val)0.2f", 'decimal' : '.', 'thousands_sep': ','},
        'CZK' : {'symbol': u'Kč', 'positive' : u"%(val)0.0f,- Kč", 'negative': u"-%(val)0.f Kč", 'decimal' : ',', 'thousands_sep': ' '},
        'EUR' : {'symbol': u'€', 'positive' : u"€%(val)0.2f", 'negative': u"-€%(val)0.2f", 'decimal' : ',', 'thousands_sep': ' '},
    })

DEFAULT_CURRENCY = getattr(settings, 'DEFAULT_CURRENCY', 'CZK')

