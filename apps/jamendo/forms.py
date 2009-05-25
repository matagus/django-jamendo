#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _


class NameSearchForm(forms.Form):
    name = forms.CharField(required=False, label=_("Search by name"))