import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.files import File as DjangoFile
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from catalog.models import Product, ProductImage, Category, CategoryImage

PRODUCTS = 'Products'
CATEGORIES = 'Categories'


def get_folder(folder):
    """ get or create folder """
    if Folder.objects.filter(name=folder).count() > 0:
        folder = Folder.objects.get(name=folder)
    else:
        folder = Folder(name=folder, parent=None)
        folder.save()
    return folder

def save_image(folder, dir, filename, user):
    base, _ =  os.path.splitext(filename)
    filepath = os.path.join(dir, filename)
    file = DjangoFile(open(filepath, 'rb'), name=filename)
    image = Image(owner=user, folder=folder, name=base, original_filename=filename, file=file, is_public=True)
    image.save()
    return image
                    
class Command(BaseCommand):
    help = 'Assign pictures in given folder to existing products'
    args = "folder"
        
        
    def handle(self, *fixture_labels, **options):

        if len(fixture_labels) > 0:
            dirpath = fixture_labels[0]
            if not os.path.exists(dirpath):
                print 'Path does not exist:', dirpath
                return
            used = []
            pictures = os.listdir(dirpath) 
            products = [prod.slug for prod in Product.objects.active()]
            categories = [cat.slug for cat in Category.objects.active()]

            prod_folder = get_folder(PRODUCTS)
            cat_folder = get_folder(CATEGORIES)
            
            user = User.objects.get(is_superuser=True)
            
            for filename in pictures:
                base, _ =  os.path.splitext(filename)
                
                
                if base in categories:
                    
                    image = save_image(cat_folder, dirpath, filename, user)
                    cat = Category.objects.get(slug=base)
                    if CategoryImage.objects.filter(category=cat, image=image, sort=0).count():
                        ci = CategoryImage.objects.get(category=cat, image=image)
                        ci.image = image
                        ci.save(force_update=True)
                    else:
                        ci = CategoryImage(category=cat, image=image)
                        try:
                            ci.save(force_insert=True)
                        except IntegrityError:
                            print 'Category:', cat, 'Image:', image, 'ci:', ci
                            
                    used.append(filename)
                        
                elif base in products:
                    
                    image = save_image(prod_folder, dirpath, filename, user)
                    
                    product = Product.objects.get(slug=base)
                    if ProductImage.objects.filter(product=product, image=image, sort=0).count():
                        pi =  ProductImage.objects.get(product=product, image=image)
                        pi.image = image
                        pi.save(force_update=True)
                    else:
                        pi =  ProductImage(product=product, image=image)
                        try:
                            pi.save(force_insert=True)
                        except IntegrityError:
                            print 'Product:', product
                            print 'Image:', image
                            print 'pi:', pi
                        
                    used.append(filename)

            print len(pictures), 'pictures'
            #print len(products), 'products'
            print len(used), 'used'
            print 'Unused:', len(pictures) - len(used)
            #for n in sorted(list(set(pictures)-set(used))):
            #    print n
