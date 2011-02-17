from decimal import Decimal, InvalidOperation
from django import template
from django.utils.safestring import mark_safe
from catalog.utils import moneyfmt
import logging

log = logging.getLogger("shop.currency")

register = template.Library()


def _stripquotes(val):
    stripping = True
    while stripping:
        stripping = False
        if val[0] in ('"', "'"):
            val = val[1:]
            stripping = True
        if val[-1] in ('"', "'"):
            val = val[:-1]
            stripping = True

    return val

def get_filter_args(argstring, keywords=(), intargs=(), boolargs=(), stripquotes=False):
    """Convert a string formatted list of arguments into a kwargs dictionary.
    Automatically converts all keywords in intargs to integers.

    If keywords is not empty, then enforces that only those keywords are returned.
    Also handles args, which are just elements without an equal sign

    ex:
    in: get_filter_kwargs('length=10,format=medium', ('length'))
    out: (), {'length' : 10, 'format' : 'medium'}
    """
    args = []
    kwargs = {}
    if argstring:
        work = [x.strip() for x in argstring.split(',')]
        work = [x for x in work if x != '']
        for elt in work:
            parts = elt.split('=', 1)
            if len(parts) == 1:
                if stripquotes:
                    elt=_stripquotes(elt)
                args.append(elt)

            else:
                key, val = parts
                val = val.strip()
                if stripquotes and val:
                    val=_stripquotes(val)

                key = key.strip()
                if not key: continue
                key = key.lower().encode('ascii')

                if not keywords or key in keywords:
                    if key in intargs:
                        try:
                            val = int(val)
                        except ValueError:
                            raise ValueError('Could not convert value "%s" to integer for keyword "%s"' % (val, key))
                    if key in boolargs:
                        val = val.lower()
                        val = val in (1, 't', 'true', 'yes', 'y', 'on')
                    kwargs[key] = val
    return args, kwargs

def currency(value, args=""):
    """Convert a value to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    wrapcents:tag to wrap the part after the decimal point

    Usage:
        val|currency
        val|currency:'places=2'
        val|currency:'places=2:wrapcents=sup'
    """

    if value == '' or value is None:
        return value

    args, kwargs = get_filter_args(args,
        keywords=('places','curr', 'wrapcents'),
        intargs=('places',), stripquotes=True)

    try:
        value = Decimal(str(value))
    except InvalidOperation:
        log.error("Could not convert value '%s' to decimal", value)
        raise

    return mark_safe(moneyfmt(value, **kwargs))

register.filter('currency', currency)
currency.is_safe = True
