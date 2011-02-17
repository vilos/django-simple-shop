'''
Models that represent
basic product and catalog information for an ecommerce
application. 
'''
from datetime import date
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from filer.fields.image import FilerImageField
from cms.models.fields import PlaceholderField
from fields import CurrencyField
from utils import moneyfmt
from shop.settings import SHOP_PRICE_INCLUDES_TAX, DEFAULT_CURRENCY
from settings import CATEGORY_TEMPLATES

class ActiveManager(models.Manager):
    
    def active(self, **kwargs):
        return self.filter(active=True, **kwargs)
    

class CategoryManager(ActiveManager):
    
    def root_categories(self, **kwargs):
        """Get all root categories."""
        return self.active().filter(parent__isnull=True, **kwargs)
    
        
class Category(models.Model):
    '''
    The ``Category`` model represents a category within a specific
    ``Catalog`` object. Categories contain a ForeignKey to their
    catalog, as well as an optional ForeignKey to another category
    that will serve as a parent category.
    '''
    active = models.BooleanField(_('is active'), default=True)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', db_index=True)
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=150)
    path = models.CharField(_("Path"), max_length=255, blank=True, db_index=True)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    description = models.TextField(blank=True)
    template = models.CharField(_(u"Category template"), max_length=255, 
                                blank=True, null=True, 
                                choices=CATEGORY_TEMPLATES,
                                default=CATEGORY_TEMPLATES[0][0])
    separator = '::'
    
    objects = CategoryManager()
    
    class Meta:
        ordering = ['parent__id', 'ordering', 'name']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        
    def __unicode__(self):
        name_list = [cat.name for cat in self.get_ancestors()]
        name_list.append(self.name)
        return self.separator.join(name_list)

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.category_view', [self.path])

    def active_products(self, include_children=False, **kwargs):
        if not include_children:
            qry = self.products.all()
        else:
            cats = self.get_descendants(include_self=True)
            qry = Product.objects.filter(categories__in=cats)

        return qry.filter(active=True, **kwargs)
    
    @property
    def main_image(self):
        img = False
        if self.images.count() > 0:
            img = self.images.order_by('sort')[0]
        else:
            if self.parent_id and self.parent != self:
                img = self.parent.main_image

        if not img:
            #This should be a "Image Not Found" placeholder image
            try:
                img = CategoryImage.objects.filter(category__isnull=True).order_by('sort')[0]
            except IndexError:
                pass
        return img

    def get_children(self):
        """
        :returns: A queryset of all the node's children
        """
        return self.__class__.objects.filter(parent=self)

    def get_ancestors(self):
        """
        :returns: A *list* containing the current node object's ancestors,
            starting by the root node and descending to the parent.
        """
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        ancestors.reverse()
        return ancestors

    def get_root(self):
        """
        :returns: the root node for the current node object.
        """
        ancestors = self.get_ancestors()
        if ancestors:
            return ancestors[0]
        return self

    def _flatten(self, L):
        """
        Taken from a python newsgroup post
        """
        if type(L) != type([]): return [L]
        if L == []: return L
        return self._flatten(L[0]) + self._flatten(L[1:])

    def _recurse_for_children(self, node):
        children = []
        children.append(node)
        for child in node.children.active():
            if child != self:
                children_list = self._recurse_for_children(child)
                children.append(children_list)
        return children

    def get_descendants(self, include_self=False):
        """
        Gets a list of all of the children categories.
        """
        children_list = self._recurse_for_children(self)
        # first item is self
        ix = 0 if include_self else 1
        flat_list = self._flatten(children_list[ix:])
        return flat_list
    
    def save(self, *args, **kwargs):
        current_path = self.path
        slug = u'%s' % self.slug
        if self.parent:
            self.path = u'%s/%s' % (self.parent.path, slug)
        else:
            self.path = u'%s' % slug
                        
        super(Category, self).save(*args, **kwargs)
        
        # Update descendants only if path changed
        if current_path != self.path:
            for child in self.get_children():
                child.path = child.path.replace(current_path, self.path, 1)
                child.save()
                
class CategoryImage(models.Model):
    """
    Pictures for a category.
    """
    category = models.ForeignKey(Category, null=True, blank=True, related_name="images")
    image = FilerImageField(null=True, blank=True, default=None)
    caption = models.CharField(_("Caption"), max_length=255,
        null=True, blank=True)
    icon = models.BooleanField(_("Icon"), default=False)
    sort = models.IntegerField(_("Sort Order"), default=0)

    def __unicode__(self):
        if self.category:
            return u"Image of %s - %d" % (self.category.slug, self.sort)
        else:
            return u"%s" % self.image

    class Meta:
        ordering = ['sort']
        unique_together = (('category', 'sort'),)
        verbose_name = _("Category Image")
        verbose_name_plural = _("Category Images")
        
class Product(models.Model):
    '''
    The ``Product`` model represents a particular item in a catalog of
    products. It contains information about the product for sale,
    which is common to all items in the catalog. These include, for
    example, the item's price, manufacturer, an image or photo, a
    description, etc.
    '''
    name = models.CharField(_("Full Name"), max_length=255, blank=False,
                            help_text=_("This is what the product will be called in the default site language."))
    slug = models.SlugField(_("Item No."), max_length=255, blank=True, unique=True,
        help_text=_("Used for URLs, auto-generated from name if blank"), )
    sku = models.CharField(_("Model No."), max_length=255, blank=True, null=True,
        help_text=_("Defaults to slug if left blank."))
    short_description = models.TextField(_("Short description of product"), 
                                         help_text=_("This should be a 1 or 2 line description for use in product listing screens"), 
                                         max_length=200, default='', blank=True)
    description = PlaceholderField("product_description")
        
    active = models.BooleanField(_("Active"), default=True, help_text=_("Is product Active?"))
    categories = models.ManyToManyField(Category, blank=True, null=True,
                                        verbose_name=_('Categories'), related_name='products')
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in category display"))
    featured = models.BooleanField(_("Featured Item"), default=False, help_text=_("Featured items will show on the front page"))
    date_added = models.DateField(_("Date added"), null=True, blank=True, default=date.today)

    objects = ActiveManager()
    
    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('catalog.views.product_detail', (), {'slug': self.slug})

    def save(self, *args, **kw):

        if self.name and not self.slug:
            self.slug = slugify(self.name, instance=self)

        if not self.sku:
            self.sku = self.slug
            
        super(Product, self).save(*args, **kw)

    @property
    def main_image(self):
        img = None
        if self.images.count() > 0:
            img = self.images.order_by('sort')[0]
        
        if not img:
            #This should be a "Image Not Found" placeholder image
            try:
                img = ProductImage.objects.filter(product__isnull=True).order_by('sort')[0]
            except IndexError:
                pass
        
        return img
    
    def get_price(self, **kwargs):
        return self.prices.active().filter(**kwargs).latest()

    @property
    def price(self):
        return self.get_price(currency=DEFAULT_CURRENCY)
    
    @property
    def original_price(self):
        return self.get_price(currency=DEFAULT_CURRENCY, is_sale=False)
    
    @property
    def sale_price(self):
        return self.get_price(currency=DEFAULT_CURRENCY, is_sale=True)
    
    @property
    def discount(self):
        original = self.original_price
        if not original:
            return 0
        sale = self.sale_price or original
        return " %s%%" % round(100 * (original.unit_price - sale.unit_price) / original.unit_price, 2)
        
    
class ProductDetailManager(models.Manager):
    def by_group(self, group, **kw):
        return self.filter(attribute__group=group, **kw)
    
    def in_first_group(self, **kw):
        group = AttributeGroup.objects.all()[0]
        return self.by_group(group=group)
    
class ProductDetail(models.Model):
    '''
    The ``ProductDetail`` model represents information unique to a
    specific product. This is a generic design that can be used to
    extend the information contained in the ``Product`` model with
    specific, extra details.
    '''
    product = models.ForeignKey('Product', related_name='details')
    attribute = models.ForeignKey('ProductAttribute')
    value = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    objects = ProductDetailManager()
    
    def __unicode__(self):
        return u'%s (%s): %s' % (self.attribute.name, self.product.name, self.value)

    class Meta:        
        unique_together = (('attribute', 'product'),)
        verbose_name = _("Product Detail")
        verbose_name_plural = _("Products Details")

class ProductAttributeManager(models.Manager):
    
    def by_group(self, group, **kw):
        return self.filter(group=group, **kw)
    
class ProductAttribute(models.Model):
    '''
    The ``ProductAttribute`` model represents a class of feature found
    across a set of products. It does not store any data values
    related to the attribute, but only describes what kind of a
    product feature we are trying to capture.

    Possible attributes include things like materials, colors, sizes,
    and many, many more.
    '''
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    group = models.ForeignKey("AttributeGroup", blank=True, null=True)
    sort = models.IntegerField(_("Sort Order"), default=0)
    
    objects = ProductAttributeManager()
    
    def __unicode__(self):
        return u'%s' % self.name

    def __repr__(self):
        return u"<Attribute: %s>" % self.name

    class Meta:
        ordering = ['sort', 'name']
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")


class AttributeGroup(models.Model):
    """
    A set of attributes of an item.
    """
    name = models.CharField(_("Attribute Group"), max_length=100, unique=1)
    sort = models.IntegerField(_("Sort Order"), help_text=_("The display order for this group."), default=0)

    def __unicode__(self):
        return self.name
    
    def __repr__(self):
        return u"<Attribute Group: %s>" % self.name

    class Meta:
        ordering = ['sort', 'name']
        verbose_name = _("Attribute Group")
        verbose_name_plural = _("Attribute Groups")


class ProductImage(models.Model):
    """
    Pictures of a product item.
    """
    product = models.ForeignKey(Product, null=True, blank=True, related_name="images")
    image = FilerImageField(null=True, blank=True, default=None)
    caption = models.CharField(_("Optional caption"), max_length=255,
        null=True, blank=True)
    sort = models.IntegerField(_("Sort Order"), default=0)

    def __unicode__(self):
        if self.product:
            return u"Image of %s - %d" % (self.product.slug, self.sort)
        else:
            return u"%s" % self.image

    class Meta:
        ordering = ['sort']
        unique_together = (('product', 'sort'),)
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

class TaxClass(models.Model):
    name = models.CharField(_('name'), max_length=100)
    rate = models.DecimalField(_('rate'), max_digits=10, decimal_places=2)
    priority = models.PositiveIntegerField(_('priority'), default=0,
        help_text = _('Used to order the tax classes in the administration interface.'))

    class Meta:
        ordering = ['-priority']
        verbose_name = _('tax class')
        verbose_name_plural = _('tax classes')

    def __unicode__(self):
        return self.name
    
    def process(self, price, **kwargs):
        return price * (self.rate/100)
    
    def extract(self, price_with_tax, **kwargs):
        if self.rate > 0:
            return  price_with_tax / (1 + 100/self.rate)
        else:
            return price_with_tax
        
class ProductPriceManager(models.Manager):
    def active(self, **kw):
        return self.filter(
            Q(active=True),
            Q(valid_from__lte=date.today()),
            Q(valid_until__isnull=True) | Q(valid_until__gte=date.today()), **kw)
        
                
class ProductPrice(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('product'), related_name='prices')
    currency = CurrencyField()
    _unit_price = models.DecimalField(_('unit price'), max_digits=18, decimal_places=10)
    tax_included = models.BooleanField(_('tax included'),
        help_text=_('Is tax included in given unit price?'),
        default=SHOP_PRICE_INCLUDES_TAX)
    tax_class = models.ForeignKey(TaxClass, verbose_name=_('tax class'))

    active = models.BooleanField(_('is active'), default=True)
    valid_from = models.DateField(_('valid from'), default=date.today)
    valid_until = models.DateField(_('valid until'), blank=True, null=True)

    is_sale = models.BooleanField(_('is sale'), default=False,
        help_text=_('Set this if this price is a sale price.'))

    class Meta:
        get_latest_by = 'id'
        ordering = ['-valid_from']
        verbose_name = _('product price')
        verbose_name_plural = _('product prices')

    objects = ProductPriceManager()

    def __unicode__(self):
        return moneyfmt(self.unit_price, self.currency)

    @property
    def tax_rate(self):
        return self.tax_class.rate

    @property
    def tax_name(self):
        return self.tax_class.name
    
    @property
    def unit_tax(self):
        return self.tax_class.process(self.unit_price_excl_tax) 

    @property
    def unit_price_incl_tax(self):
        if self.tax_included:
            return self._unit_price
        return self._unit_price + self.tax_class.process(self._unit_price)

    @property
    def unit_price_excl_tax(self):
        if not self.tax_included:
            return self._unit_price
        return self._unit_price - self.tax_class.extract(self._unit_price)

    @property
    def unit_price(self):
        if self.tax_included:
            return self.unit_price_incl_tax
        else:
            return self.unit_price_excl_tax
        