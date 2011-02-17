from django.contrib import admin
from models import Customer, Address

class CustomerAdmin(admin.ModelAdmin):
    
    list_display = ('__unicode__', 'email', 'phone', 'shipping_address')
    list_display_links=('__unicode__',)
    readonly_fields = ('user', 'session') 
    
admin.site.register(Customer)
admin.site.register(Address)

