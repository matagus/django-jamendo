#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from jamendo.views import ArtistsList, ArtistShow, AlbumsList, AlbumShow,\
    TagsCloud, TagShow, CountriesList, CountryShow, LicensesList, LicenseShow,\
    CitiesList, CityShow
from jamendo.feeds import ArtistsFeed, AlbumsFeed, AlbumsForFeed


urlpatterns = patterns("jamendo.views",
    # artists urls
    url(r"^artists/$", ArtistsList(), name="jamendo_artists"),
    url(r"^artists/(?P<pk>\d+)/$", ArtistShow(), name="jamendo_artist"),
    url(r"^artists/juid/(?P<juid>\d+)/$", ArtistShow(), name="jamendo_artist_juid"),
    url(r"^artists/mbgid/(?P<mbgid>[-\d\w]+)/$", ArtistShow(), name="jamendo_artist_mbgid"),

    # albums urls
    url(r"^albums/$", AlbumsList(), name="jamendo_albums"),
    url(r"^albums/(?P<pk>\d+)/$", AlbumShow(), name="jamendo_album"),
    url(r"^albums/juid/(?P<juid>\d+)/$", AlbumShow(), name="jamendo_album_juid"),
    url(r"^albums/mbgid/(?P<mbgid>[-\d\w]+)/$", AlbumShow(), name="jamendo_album_mbgid"),

    # tags urls
    url(r"^tags_cloud/$", TagsCloud(), name="jamendo_tagscloud"),
    url(r"^tags/(?P<tag>\w+)/$", TagShow(), name="jamendo_tag"),
    
    # countries urls
    url(r"^countries/$", CountriesList(), name="jamendo_countries"),
    url(r"^countries/(?P<code>\w+)/$", CountryShow(), name="jamendo_country"),
    url(r"^countries/juid/(?P<juid>\d+)/$", CountryShow(), name="jamendo_country_juid"),

    # cities urls
    url(r"^cities/$", CitiesList(), name="jamendo_cities"),
    url(r"^cities/(?P<pk>\w+)/$", CityShow(), name="jamendo_city"),
    url(r"^cities/juid/(?P<juid>\d+)/$", CityShow(), name="jamendo_city_juid"),
    
    # licenses urls
    url(r"^licenses/$", LicensesList(), name="jamendo_licenses"),
    url(r"^licenses/(?P<pk>\d+)/$", LicenseShow(), name="jamendo_license"),
    url(r"^licenses/juid/(?P<juid>\d+)/$", LicenseShow(), name="jamendo_license_juid"),
)

urlpatterns += patterns("",
    (r"^feeds/(.*)/$", "django.contrib.syndication.views.feed", {
        "feed_dict": {"artists": ArtistsFeed, "albums": AlbumsFeed, "albumsfor": AlbumsForFeed}
    }),
)
