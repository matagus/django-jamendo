#!/usr/bin/python
# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import os.path

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name = "django-jamendo",
    version = "0.1",
    packages = find_packages('apps'),
    package_dir = {'':'apps'},
    #package_data = {
    #    '': ['INSTALL','LICENSE','README','TODO','ez_setup.py'],
    #    'jamendo': ['templates/*.html', 'templates/jamendo/*.html'],
    #},
    include_package_data = True,
    #scripts = [''], #TODO: Put here the clever import scripts ;-)
    install_requires = [
        'django>=1.1',
        'tagging',
        'django-pagination'
    ],
    author = "Matías Agustín Méndez",
    author_email = "matagus[at]gmail.com",
    description = read('README'),
    license = 'New BSD',
    keywords = 'django jamendo music cc',
    url = 'http://github.com/matagus/django-jamendo',
    classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
)
