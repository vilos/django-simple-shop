from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.sessions.backends.file import SessionStore
from django.test import TestCase

from catalog.models import TaxClass, Product, ProductPrice
from shop.models import Shop, Order, OrderItem

class CartModelsWithTaxTestCase(TestCase):
    """
    """
    
    tax_included=True
    
    def setUp(self):
        """
        """
        self.tax = TaxClass(name="20%", rate=Decimal('20.0'))
        self.tax.save()
        self.p1 = Product.objects.create(name="Product 1", slug="product-1")
        self.p2 = Product.objects.create(name="Product 2", slug="product-2")
        self.p1.save()
        self.p2.save()
        
        price1 = ProductPrice(product=self.p1, _unit_price=Decimal('10.0'), currency='CZK', tax_class=self.tax, tax_included=self.tax_included)
        price2 = ProductPrice(product=self.p2, _unit_price=Decimal('100.0'), currency='CZK', tax_class=self.tax, tax_included=self.tax_included)
        price1.save()
        price2.save()
        
        self.cart = Order()
        self.cart.save()
        
        item1 = OrderItem(order=self.cart, product=self.p1, quantity=1)
        item2 = OrderItem(order=self.cart, product=self.p2, quantity=1)
        item1.save()
        item2.save()
        
        self.cart.recalculate_totals()
        self.cart.save()
        
    def test_tax_detail(self):
        
        tax_detail = self.cart.tax_detail
        self.assertEqual("%.2f" % float(tax_detail['20%']), "%.2f" % 18.33)
    
    def test_get_subtotal(self):
        """
        """
        subtotal = self.cart.sub_total
        self.assertEqual("%.2f" % float(subtotal), "%.2f" % 91.67)
        
    def test_get_total(self):
        """
        """
        total = self.cart.total
        self.assertEqual("%.2f" % float(total), "%.2f" % 110.0)
        
    def test_tax(self):
        """
        """
        tax = self.cart.tax
        self.assertEqual("%.2f" % float(tax), "%.2f" % 18.33)
        
    def test_get_qty_of_items(self):
        """
        """
        qty = self.cart.items_qty()
        self.assertEqual(qty, 2)
        
    def test_get_items_count(self):
        """
        """
        n = self.cart.items_count()
        self.assertEqual(n, 2)
        
        
class CartModelsWithoutTaxTestCase(CartModelsWithTaxTestCase):
    """
    """
    
    tax_included=False
        
    def test_tax_detail(self):
        
        tax_detail = self.cart.tax_detail
        self.assertEqual("%.2f" % float(tax_detail['20%']), "%.2f" % 22.0)
    
    def test_get_subtotal(self):
        """
        """
        subtotal = self.cart.sub_total
        self.assertEqual("%.2f" % float(subtotal), "%.2f" % 110.0)
        
    def test_get_total(self):
        """
        """
        total = self.cart.total
        self.assertEqual("%.2f" % float(total), "%.2f" % 132.0)
        
    def test_tax(self):
        """
        """
        tax = self.cart.tax
        self.assertEqual("%.2f" % float(tax), "%.2f" % 22.0)
        
    def test_get_qty_of_items(self):
        """
        """
        qty = self.cart.items_qty()
        self.assertEqual(qty, 2)
        
    def test_get_items_count(self):
        """
        """
        n = self.cart.items_count()
        self.assertEqual(n, 2)