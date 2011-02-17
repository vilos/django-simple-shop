# coding: utf-8
from django.conf import settings


CATEGORY_TEMPLATES = getattr(settings, 'CATEGORY_TEMPLATES', (
    ('catalog/product_list.html', 'Product list'),
    ('catalog/product_detail.html', 'Product detail'))
)

ENABLE_FEATURED_PRODUCTS = getattr(settings, 'ENABLE_FEATURED_PRODUCTS', True)
