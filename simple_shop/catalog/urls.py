from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('catalog.views',
    url(r'^$', 'category_view', {'path':''}, name="catalog_featured_view"),
    url(r'^c/(?P<path>([-\w]+/?)*)$', 
        'category_view', name="catalog_category_view"),
    url(r'^p/(?P<slug>[-\w]+)/$', 'product_detail', name="catalog_product_detail"),
)