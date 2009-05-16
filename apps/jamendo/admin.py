#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from jamendo.models import Artist, Album, Track, TagInfo, License,\
    Language, Country, State, City, Playlist, Radio, JamendoUser, Genre, Review

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Track)
admin.site.register(TagInfo)
admin.site.register(License)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(City)
admin.site.register(Playlist)
admin.site.register(Radio)
admin.site.register(JamendoUser)
admin.site.register(Genre)
admin.site.register(Review)

