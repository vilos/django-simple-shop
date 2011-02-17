import os, csv
from django.core.management.base import BaseCommand
from django.forms.models import fields_for_model
from catalog.models import Category

      
class Command(BaseCommand):
    help = 'Imports categories from csv file'
    args = "csvfile "

    def get_value(self, column, row):        
        return row[self.header.index(column)]
        
    def resolve_parent(self, column, row):
        pid = self.get_value(column, row)
        if pid:
            parent = Category.objects.get(id=pid)
        else:
            parent = None
        return parent
        
    def handle(self, *fixture_labels, **options):

        if len(fixture_labels) > 0:
            path = fixture_labels[0]
            if not os.path.exists(path):
                print 'Path does not exist:', path
                return
            
            fields = fields_for_model(Category)
            
            reader = csv.reader(open(path), delimiter=";")
            self.header = reader.next()
            columns =  list(set(fields.keys()) & set(self.header))
            if 'id' in self.header:
                key = 'id'
            elif 'slug' in self.header:
                key = 'slug'
            else:
                raise ValueError('Either id or slug column must be present in csv data.')
            
            for row in reader:
                pk = self.get_value(key, row)
                q = {key: pk}
                data = dict([(c, getattr(self, 'resolve_'+c, self.get_value)(c, row)) for c in columns])
                cat = None
                if Category.objects.filter(**q).count() > 0:
                    Category.objects.filter(**q).update(**data)
                    cat = Category.objects.get(**q)
                else:
                    if key not in data:
                        data[key] = pk
                    cat = Category(**data)

                if cat:
                    cat.save()
