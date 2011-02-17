from menus.base import Menu, NavigationNode, Modifier
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _
from models import Category, CategoryImage

class CatalogMenu(Menu):

    name = _("Catalog")
    
    def get_nodes(self, request):
        nodes = []
        for category in Category.objects.all().order_by("parent", "ordering"):
            nodes.append(NavigationNode(title=category.name, 
                                        url=category.get_absolute_url(), 
                                        id=category.pk, 
                                        parent_id=category.parent_id,
                                        attr=dict(slug=category.slug)))

        return nodes

class CategoryIcon(Modifier):
    """
    navigation modifier that adds icon attribute
    """
    icons = {}
    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        if breadcrumb or not post_cut:
            return nodes
        ns = CatalogMenu.__name__
        if not self.icons:
            for ci in CategoryImage.objects.filter(icon=True):
                self.icons[ci.category.pk] = ci.image.file.url 
        if self.icons:
            for node in nodes:
                #print node.id, node.title, ', ns:', getattr(node, 'namespace', 'None')
                if node.namespace == ns and self.icons.get(node.id, None):
                    node.attr['icon'] = self.icons.get(node.id)
        return nodes
    
menu_pool.register_menu(CatalogMenu)
menu_pool.register_modifier(CategoryIcon)