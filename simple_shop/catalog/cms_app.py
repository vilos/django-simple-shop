from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _
from menu import CatalogMenu


class CatalogHook(CMSApp):
    name = _("Catalog")
    urls = ["catalog.urls"]
    menus = [CatalogMenu]

    
apphook_pool.register(CatalogHook)
