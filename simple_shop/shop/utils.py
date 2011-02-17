import decimal
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import _get_queryset


def make_cache_key(klass, **kwargs):
    return '-'.join([klass.__name__.lower()] + [str(kwargs[k]) for k in sorted(kwargs.keys())])

def cache_get_object_or_404(klass, *args, **kwargs):
    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    cache_key = make_cache_key(klass, **kwargs)
    object = cache.get(cache_key)
    if object is not None:
        return object

    queryset = _get_queryset(klass)
    try:
        object = queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)
    else:
        cache.set(cache_key, object)
        return object

def cache_get_object(klass, *args, **kwargs):
    """
    Uses get() to return an object, or returns None if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """
    cache_key = make_cache_key(klass, **kwargs)
    object = cache.get(cache_key)
    if object is not None:
        return object

    queryset = _get_queryset(klass)

    try:
        object = queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    else:
        cache.set(cache_key, object)
        return object
    

def cache_remove_object(klass, **kwargs):
    cache_key = make_cache_key(klass, **kwargs)
    cache.delete(cache_key)
    

TWOPLACES = decimal.Decimal('0.01')

def round_cents(x):
    return x.quantize(TWOPLACES, decimal.ROUND_FLOOR)
    
