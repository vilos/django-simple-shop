from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.simple import redirect_to
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from models import Category, Product
from settings import ENABLE_FEATURED_PRODUCTS

def featured_view(request, template="catalog/product_list.html"):
    
    if not ENABLE_FEATURED_PRODUCTS:
        category = Category.objects.root_categories()[0] 
        return redirect_to(request, category.get_absolute_url())
        
    featured = Product.objects.filter(active=True, featured=True)
    cat = Category(name=_('Featured products'))
    data = { 
        'category' : cat,
        'products' : featured,
    }
    
    return render_to_response(template, RequestContext(request, data))


def category_view(request, path='', template='catalog/product_list.html'): 
    """Display the category, its child categories, and its products.

    Parameters:
     - path: url path of category
    """
    
    if path:
        category = get_object_or_404(Category, path=path)
        template = category.template
        products = list(category.active_products(include_children=True))        
    else:
        if ENABLE_FEATURED_PRODUCTS:
            # virtual category to get a title
            category = Category(name=_('Featured products'))
            products = Product.objects.filter(active=True, featured=True)
        else:
            category = Category.objects.root_categories()[0] 
            return redirect_to(request, category.get_absolute_url())            
    
    data = {
        'category': category, 
        'products' : products,
    }
    
    return render_to_response(template, RequestContext(request, data))


def product_detail(request, slug, template="catalog/product_detail.html"):
    
    product = get_object_or_404(Product, slug=slug)
    data = dict(product=product)
    return render_to_response(template, RequestContext(request, data))