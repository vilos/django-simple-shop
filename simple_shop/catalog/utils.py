from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ImproperlyConfigured
from shop.settings import CURRENCY_FORMATS, DEFAULT_CURRENCY
import logging
import re

log = logging.getLogger('catalog.utils')

# Defined outside the function, so won't be recompiled each time
# moneyfmt is called.
# This is required because some currencies might include a . in the description
decimal_separator = re.compile(r'(\d)\.(\d)')

#####################################
# http://code.activestate.com/recipes/498181-add-thousands-separator-commas-to-formatted-number/
# Code from Michael Robellard's comment made 28 Feb 2010
# Modified for leading +, -, space on 1 Mar 2010 by Glenn Linderman
# 
# Tail recursion removed and  leading garbage handled on March 12 2010, Alessandro Forghieri

def split_thousands(s, tSep=',', dSep='.'):
    '''Splits a general float on thousands. GIGO on general input'''
    if s == None:
        return 0
    if not isinstance(s, basestring):
        s = unicode(s)

    cnt=0
    numChars=dSep+'0123456789'
    ls=len(s)
    while cnt < ls and s[cnt] not in numChars: cnt += 1

    lhs = s[0:cnt]
    s = s[cnt:]
    if dSep == '':
        cnt = -1
    else:
        cnt = s.rfind(dSep)
    if cnt > 0:
        rhs = dSep + s[cnt+1:]
        s = s[:cnt]
    else:
        rhs = ''

    splt=''
    while s != '':
        splt= s[ -3: ] + tSep + splt
        s = s[ :-3 ]

    return lhs + splt[ :-1 ] + rhs


# from satchmo l10n.utils moneyfmt

def moneyfmt(val, currency_code=None, thousands_sep='', wrapcents=''):
    """Formats val according to the currency settings for the desired currency """
    if val is None or val == '':
        val = Decimal('0')
    
    currencies = CURRENCY_FORMATS
    currency = None
    
    if currency_code:
        currency = currencies.get(currency_code, None)
        if not currency:
            log.warn('Could not find currency code definitions for "%s", please look at l10n.l10n_settings for examples.')
    
    if not currency:
        default_currency_code = DEFAULT_CURRENCY
    
        if not default_currency_code:
            log.fatal("No default currency code set in L10N_SETTINGS")
            raise ImproperlyConfigured("No default currency code set in L10N_SETTINGS")
    
        if currency_code == default_currency_code:
            raise ImproperlyConfigured("Default currency code '%s' not found in currency_formats in L10N_SETTINGS", currency_code)
    
        return moneyfmt(val, currency_code=default_currency_code, wrapcents=wrapcents)
    
    # here we are assured we have a currency format
    
    if val>=0:
        key = 'positive'
    else:
        val = abs(val)
        key = 'negative'
    
    fmt = currency[key]
    formatted = fmt % { 'val' : val }
    
    sep = currency.get('decimal', '.')
    thousands_sep = currency.get('thousands_sep', '')
    
    if sep != '.':
        formatted = decimal_separator.sub(r'\1%s\2' % sep, formatted)
    
    if thousands_sep:
        formatted = split_thousands(formatted, thousands_sep, sep)
        
    if wrapcents:
        pos = formatted.rfind(sep)
        if pos>-1:
            pos +=1
            formatted = u"%s<%s>%s</%s>" % formatted[:pos], wrapcents, formatted[pos:], wrapcents
    
    return formatted

def round(d, digits=0):
    """
    Symmetric Arithmetic Rounding for decimal numbers

    d       - Decimal number to round
    digits  - number of digits after the point to leave

    For example:
    >>> round(Decimal("234.4536"), 3)
    Decimal("234.454")
    >>> round(Decimal("234.4535"), 3)
    Decimal("234.454")
    >>> round(Decimal("234.4534"), 3)
    Decimal("234.453")
    >>> round(Decimal("-234.4535"), 3)
    Decimal("-234.454")
    >>> round(Decimal("234.4535"), -1)
    Decimal("2.3E+2")
    """
    return d.quantize(Decimal("1") / (Decimal('10') ** digits), ROUND_HALF_UP)