#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponseNotAllowed, HttpResponseBadRequest, Http404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from tagging.models import Tag, TaggedItem
from jamendo.models import Artist, Album, License, Country, Track
from jamendo.forms import NameSearchForm


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
    
    def get_queryset(self, request):
        raise NotImplementedError

    def GET(self, request, *args, **kwargs):
        self.form = NameSearchForm(request.GET)
        
        params_dict = self.get_params_dict()
        params_dict.update({
            "queryset": self.get_queryset(request),
            "form": self.form
        })
        
        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class ShowView(BaseView):

    def __init__(self, model, *args, **kwargs):
        super(ShowView, self).__init__(*args, **kwargs)
        self.model = model

    def get_instance(self, *args, **kwargs):
        if "pk" in kwargs:
            self.instance = self.model.objects.get(pk=kwargs["pk"])
        elif "juid" in kwargs:
            self.instance = self.model.objects.get(uid=kwargs["juid"])
        elif "mbgid" in kwargs:
            self.instance = self.model.objects.get(mbgid=kwargs["mbgid"])

    def GET(self, request, *args, **kwargs):
        try:
            self.get_instance(*args, **kwargs)
        except self.model.DoesNotExist:
            return Http404
        except KeyError:
            return HttpResponseBadRequest()

        if not self.instance:
            return HttpResponseBadRequest()
        
        params_dict = self.get_params_dict()
        params_dict.update({"instance": self.instance})
        
        return render_to_response(self.get_template_paths(), params_dict,
            context_instance=RequestContext(request))

class ArtistsList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(ArtistsList, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        if request.GET.get("name"):
            qs = Artist.objects.filter(name__icontains=request.GET.get("name"))
        else:
            qs = Artist.objects.all()
        qs = qs.order_by("name")
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

    def get_params_dict(self):
        albums_qs = self.instance.album_set.order_by("-release_date", "name")
        return {"albums_list": albums_qs}

class AlbumsList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(AlbumsList, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        if request.GET.get("name"):
            qs = Album.objects.filter(name__icontains=request.GET.get("name"))
        else:
            qs = Album.objects.all()
        qs = qs.select_related("artist").order_by("name")
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

    def get_queryset(self, request):
        # this qs will return a QuerySet of dict items like this:
        # {'count': 21, 'font_size': 2, 'id': 2262, 'name': u'0'}
        qs = Tag.objects.cloud_for_model(Artist)
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

    def get_instance(self, *args, **kwargs):
        self.instance = get_object_or_404(Tag, name=kwargs["tag"])

    def get_params_dict(self):
        artists_qs = TaggedItem.objects.get_by_model(Artist, (self.instance, )
            ).order_by("name")
        return {"artists": artists_qs}

class CountriesList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(CountriesList, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        if request.GET.get("name"):
            qs = Country.objects.filter(name__icontains=request.GET.get("name"))
        else:
            qs = Country.objects.exclude(code=u"")
        qs = qs.order_by("name")
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

    def get_params_dict(self):
        artists_qs = Artist.objects.filter(
                city__state__country=self.instance.code
            ).distinct().order_by("name")
        return {"artists": artists_qs}

    def get_instance(self, *args, **kwargs):
        self.instance = self.model.objects.get(code=kwargs["code"])

class LicensesList(ListView):
    
    def __init__(self, *args, **kwargs):
        super(LicensesList, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        if request.GET.get("name"):
            qs = License.objects.filter(name__icontains=request.GET.get("name"))
        else:
            qs = License.objects.all()
        qs = qs.order_by("name")
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

    def get_params_dict(self):
        return {"albums": self.instance.album_set.all()}

    def get_instance(self, *args, **kwargs):
        if "pk" in kwargs:
            self.instance = self.model.objects.get(pk=kwargs["pk"])
        elif "juid" in kwargs:
            self.instance = self.model.objects.get(uid=kwargs["juid"])