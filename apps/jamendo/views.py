#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models.query import QuerySet, ValuesListQuerySet
from django.http import HttpResponse
from django.core.serializers import serialize
from django.core.serializers.json import simplejson
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from jamendo.models import Artist, Album, Track
