import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-simple-shop",
    version = "0.1",
    author = "Viliam Segeda",
    author_email = "viliam.segeda@gmail.com",
    description = ("E-commerce application for django"),
    license = "BSD",
    url = "http://packages.python.org/django-simple-shop",
    package_dir = {'' : 'simple_shop'},
    packages=find_packages('simple_shop'),
    long_description=read('README'),
    zip_safe = False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent', 
        'Topic :: Office/Business',
    ],
)