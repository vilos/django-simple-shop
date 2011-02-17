from django.contrib import admin
from cms.admin.placeholderadmin import PlaceholderAdmin
from models import Category, CategoryImage, Product, ProductDetail, \
    ProductAttribute, AttributeGroup, ProductPrice, ProductImage, TaxClass
from forms import CategoryForm

#class CatalogAdmin(admin.ModelAdmin):
#    list_display = ('name', 'publisher', 'description', 'pub_date')
#admin.site.register(Catalog, CatalogAdmin)

class CategoryImageInline(admin.TabularInline):
    model = CategoryImage
    extra = 0
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('active', '__unicode__', 'parent', 'ordering')
    list_display_links=('__unicode__',)
    list_filter=('active', 'parent')
    list_editable=('active', 'ordering',)
    inlines=[CategoryImageInline]
    prepopulated_fields={'slug': ('name',)}
    search_fields=('name', 'description')
    form = CategoryForm
    
admin.site.register(Category, CategoryAdmin)

admin.site.register(TaxClass,
    list_display=('name', 'rate', 'priority'),
    )

class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 0
    can_delete = False

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    
class ProductDetailInline(admin.TabularInline):
    model = ProductDetail
    extra = 0
        
class ProductAdmin(PlaceholderAdmin):
    filter_horizontal=('categories',)
    inlines=[ProductDetailInline, ProductImageInline, ProductPriceInline]
    list_display=('active', 'name', 'sku', 'featured', 'ordering')
    list_editable=('ordering', 'featured')
    list_display_links=('name',)
    list_filter=('active', 'categories')
    prepopulated_fields={'slug': ('name',), 'sku': ('name',)}
    search_fields=('name', 'description')
    
    
admin.site.register(Product, ProductAdmin)

class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value')
admin.site.register(ProductDetail, ProductDetailAdmin)

class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'sort')
admin.site.register(ProductAttribute, ProductAttributeAdmin)

class AtributeGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort')
admin.site.register(AttributeGroup, AtributeGroupAdmin)