#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date

from django.conf import settings

def settings_context(request):
    """
    Makes available a template var for some interesting var in settings.py
    """
    try:
        ITEMS_PER_PAGE = settings.ITEMS_PER_PAGE
    except AttributeError:
        print "oooo"
        ITEMS_PER_PAGE = 20

    try:
        TAGS_PER_PAGE = settings.TAGS_PER_PAGE
    except AttributeError:
        TAGS_PER_PAGE = 200
    
    return {"ITEMS_PER_PAGE": ITEMS_PER_PAGE, "TAGS_PER_PAGE": TAGS_PER_PAGE}