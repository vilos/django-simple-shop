from django.contrib import admin
from models import Shop, Order

#class ShopAdmin(admin.ModelAdmin):
    
admin.site.register(Shop)


class OrderAdmin(admin.ModelAdmin):
    
    list_display = ('__unicode__', 'status', )
    list_display_links=('__unicode__',)
    readonly_fields = ('customer', 'sub_total', 'total', 'tax', 'discount', 'tax_detail', 'session', 'comments') 
admin.site.register(Order, OrderAdmin)