import os, csv
from django.core.management.base import BaseCommand
from django.forms.models import fields_for_model
from django.conf import settings
from cms.models.placeholdermodel import Placeholder
from cms.models.pluginmodel import CMSPlugin
from cms.plugins.text.models import Text
from catalog.models import Category, Product, ProductDetail, ProductAttribute


def get_or_create_attribute():
    
    try:
        attr = ProductAttribute.objects.get(name='packing')
    except ProductAttribute.DoesNotExist:
        attr = ProductAttribute(name='packing')
        attr.save()
    return attr


class Command(BaseCommand):
    help = 'Imports products from csv file'
    args = "csvfile "

    def get_value(self, column, row):        
        return row[self.header.index(column)]
        
    def resolve_short_description(self, column, row):            
        return ''

    def resolve_description(self, column, row):            
        return None

    def resolve_category(self, column, row):
        
        cats = self.get_value(column, row)
        cat = None
        if cats:
            try:
                cat = Category.objects.get(slug=cats)
            except Category.DoesNotExist:
                raise ValueError('Category %s not found.', cats)
        return cat
        
    def save_body(self, placeholder, desc):
        language = settings.LANGUAGE_CODE
        try:
            plugin = CMSPlugin.objects.get(placeholder=placeholder, position=0, language=language)
            plugin.body = desc
        except CMSPlugin.DoesNotExist:   
            plugin = CMSPlugin(language=language, 
                               plugin_type='TextPlugin',
                               position=0, 
                               placeholder=placeholder)
            plugin.save()

        if plugin:
            text = Text()
            #text.set_base_attr(plugin)
            text.pk = plugin.pk
            text.id = plugin.pk
            text.placeholder = placeholder
            text.position = plugin.position
            text.plugin_type = plugin.plugin_type
            text.tree_id = plugin.tree_id
            text.lft = plugin.lft
            text.rght = plugin.rght
            text.level = plugin.level
            text.cmsplugin_ptr = plugin
            text.publisher_public_id = None
            text.public_id = None
            text.published = False
            text.language = language
            text.body = desc
            text.save()
        
        
    def post_create(self, prod, row):
        
        short = self.get_value('short_description', row)
        if short:            
            attr = get_or_create_attribute()
            if not attr:
                raise ValueError("No attribute")
            try:
                detail = ProductDetail.objects.get(product=prod, attribute=attr)

            except ProductDetail.DoesNotExist:
                detail = ProductDetail(product=prod, attribute=attr, value='')
            detail.value = short
            detail.save()

        category = self.resolve_category('category', row)
        if category:
            prod.categories.add(category)
            
        desc = self.get_value('description', row)
        if desc:
            placeholder = prod.description
            if placeholder:
                self.save_body(placeholder, desc)
         
        
    def handle(self, *fixture_labels, **options):

        if len(fixture_labels) > 0:
            path = fixture_labels[0]
            if not os.path.exists(path):
                print 'Path does not exist:', path
                return
            
            fields = fields_for_model(Product)
            print 'fields:', fields.keys()
            reader = csv.reader(open(path), delimiter=";")
            self.header = reader.next()
            print 'header', self.header
            columns =  list(set(fields.keys()) & set(self.header))
            print 'columns:', columns
            for row in reader:
                id = self.get_value('id', row)
                data = dict([(c, getattr(self, 'resolve_'+c, self.get_value)(c, row)) for c in columns])
                prod = None
                try:
                    prod = Product.objects.get(id=id)
                except Product.DoesNotExist:
                    data['id'] = id
                    pl = Placeholder(slot='product_description')
                    pl.save()
                    data['description'] = pl 
                    prod = Product(**data)
                else:
                    Product.objects.filter(id=id).update(**data)
                    prod = Product.objects.get(id=id)

                if prod:
                    prod.save()
                    self.post_create(prod, row)
