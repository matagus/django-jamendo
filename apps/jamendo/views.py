#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from tagging.models import Tag

from jamendo.models import Artist, Album, License, Country

class BaseView(object):
    """
    Base class for all class-based views
    """
    def __init__(self, *args, **kwargs):
        super(BaseView, self).__init__(*args, **kwargs)
    
    def __call__(self, request, *args, **kwargs):
        """
        Simple request-method-based view dispatcher
        """
        view = getattr(self, request.method.upper(), "GET")
        return view(request, *args, **kwargs)

    def GET(self, request, *args, **kwargs):
        return HttpResponseNotAllowed()

    def POST(self, request, *args, **kwargs):
        return HttpResponseNotAllowed()

    def JSON(self, request, *args, **kwargs):
        return HttpResponseNotAllowed()

    def get_template_paths(self):
        raise NotImplementedError

    def get_params_dict(self):
        return {}

class ListView(BaseView):

    def __init__(self, *args, **kwargs):
        super(ListView, self).__init__(*args, **kwargs)
    
    def get_queryset(self):
        raise NotImplementedError

    def GET(self, request, *args, **kwargs):
        params_dict = self.get_params_dict()
        params_dict.update({"queryset": self.get_queryset()})
        
        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class ShowView(BaseView):

    def __init__(self, model, *args, **kwargs):
        super(ShowView, self).__init__(*args, **kwargs)
        self.model = model

    def GET(self, request, pk=None, juid=None, mbgid=None, *args, **kwargs):
        params_dict = self.get_params_dict()
        if pk:
            instance = get_object_or_404(self.model, pk=pk)
        elif juid:
            instance = get_object_or_404(self.model, uid=juid)
        elif mbgid:
            instance = get_object_or_404(self.model, mbgid=mbgid)
        else:
            return HttpResponseBadRequest()
        
        params_dict.update({"instance": instance})
        
        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class ArtistsList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(ArtistsList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = Artist.objects.all().order_by("name")
        return qs

    def get_template_paths(self):
        templates_list = ("jamendo/artists/list.html", )
        return templates_list

class ArtistShow(ShowView):
    
    def __init__(self, *args, **kwargs):
        super(ArtistShow, self).__init__(Artist, *args, **kwargs)

    def get_template_paths(self):
        templates_list = ("jamendo/artists/show.html", )
        return templates_list

class AlbumsList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(AlbumsList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = Album.objects.all().order_by("name")
        return qs

    def get_template_paths(self):
        templates_list = ("jamendo/albums/list.html", )
        return templates_list

class AlbumShow(ShowView):
    
    def __init__(self, *args, **kwargs):
        super(AlbumShow, self).__init__(Album, *args, **kwargs)

    def get_template_paths(self):
        templates_list = ("jamendo/albums/show.html", )
        return templates_list

class TagsCloud(ListView):
    
    def __init__(self, *args, **kwargs):
        super(TagsCloud, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = Tag.objects.all()
        return qs

    def get_template_paths(self):
        templates_list = ("jamendo/tags/cloud.html", )
        return templates_list

class TagShow(ShowView):

    def __init__(self, *args, **kwargs):
        super(TagShow, self).__init__(Tag, *args, **kwargs)

    def get_template_paths(self):
        templates_list = ("jamendo/tags/show.html", )
        return templates_list

    def GET(self, request, tag, *args, **kwargs):
        params_dict = self.get_params_dict()

        instance = get_object_or_404(Tag, name=tag)
        params_dict.update({"instance": instance})

        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class CountriesList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(CountriesList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = Country.objects.all().order_by("name")
        return qs

    def get_template_paths(self):
        templates_list = ("jamendo/countries/list.html", )
        return templates_list

class CountryShow(ShowView):
    
    def __init__(self, *args, **kwargs):
        super(CountryShow, self).__init__(Country, *args, **kwargs)

    def get_template_paths(self):
        templates_list = ("jamendo/countries/show.html", )
        return templates_list

    def GET(self, request, code=None, juid=None, *args, **kwargs):
        params_dict = self.get_params_dict()
        if code:
            instance = get_object_or_404(self.model, code=code)
        elif juid:
            instance = get_object_or_404(self.model, uid=juid)
        else:
            return HttpResponseBadRequest()
        params_dict.update({"instance": instance})

        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class LicensesList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(LicensesList, self).__init__(*args, **kwargs)

    def get_queryset(self):
        qs = License.objects.all().order_by("name")
        return qs

    def get_template_paths(self):
        templates_list = ("jamendo/licenses/list.html", )
        return templates_list

class LicenseShow(ShowView):
    
    def __init__(self, *args, **kwargs):
        super(LicenseShow, self).__init__(License, *args, **kwargs)

    def get_template_paths(self):
        templates_list = ("jamendo/licenses/show.html", )
        return templates_list

