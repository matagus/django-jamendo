#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib

from django.contrib.contenttypes.models import ContentType
from django.db import models

from tagging.models import Tag

class HistoryMixin(models.Model):
    # creation date time
    added_at = models.DateTimeField(auto_now_add=True)
    # last modified date time
    modified_at = models.DateTimeField(auto_now=True)
    # date time at which it was updated with jamendo data
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        get_latest_by = "modified_at"

class TaggedMixin(models.Model):
    class Meta:
        abstract = True

    def _get_tags(self):
        return Tag.objects.get_for_object(self)

    def _set_tags(self, tag_list):
        Tag.objects.update_tags(self, tag_list)

    tags = property(_get_tags, _set_tags)

class Album(HistoryMixin, TaggedMixin):
    uid = models.IntegerField(unique=True, db_index=True)
    mbgid = models.TextField(max_length=48, blank=True)
    
    name = models.TextField(blank=True, db_index=True)
    url = models.URLField()
    image = models.URLField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True, db_index=True)
    filename = models.TextField()

    genre = models.ForeignKey("Genre", null=True)
    license = models.ForeignKey("License", null=True)
    artist = models.ForeignKey("Artist")
    track_count = models.IntegerField(default=1)
    duration = models.IntegerField(default=0)
    
    class Meta:
        #db_table = u'albums'
        #order_with_respect_to = ""
        ordering = ["name", "release_date"]
        verbose_name = "album"
        verbose_name_plural = "albums"

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.artist)

    def get_tags(self):
        track_ids = self.track_set.values_list("pk", flat=True)
        content_type = ContentType.objects.get_for_model(Track)
        tags = Tag.objects.filter(
                items__content_type=content_type,
                items__object_id__in=track_ids
            ).distinct()
        return tags

    def get_mp3_url(self):
        # redirects to stream url for the first track of this album,
        # since jamendo api does not allow us to get the download url :(
        return "http://api.jamendo.com/get2/stream/album/redirect/?id=%d&streamencoding=mp31" % self.uid
    
    def get_ogg_url(self):
        # redirects to stream url for the first track of this album,
        # since jamendo api does not allow us to get the download url :(
        return "http://api.jamendo.com/get2/stream/album/redirect/?id=%d&streamencoding=ogg2" % self.uid

    def get_playlist_url(self, encoding="ogg2", ptype="m3u"):
        return "http://api.jamendo.com/get2/stream/album/%s/?id=%d&streamencoding=%s" % (ptype, self.uid, encoding)

    def get_mp3_playlist_url(self, ptype="m3u"):
        return self.get_playlist_url(encoding="mp31", ptype=ptype)
    
    def get_human_duration(self):
        return u"%d:%.2d" % (self.duration / 60, self.duration % 60)
    
class License(HistoryMixin):
    uid = models.IntegerField(unique=True, db_index=True)
    license_class = models.TextField(db_index=True)
    name = models.TextField(db_index=True)
    url = models.URLField(unique=True) # license_artwork

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.url)

class Genre(HistoryMixin):
    """
    id3 genres
    """
    code = models.TextField(unique=True, db_index=True)
    name = models.TextField(db_index=True)
    plural_name = models.TextField(blank=True, db_index=True)

    def __unicode__(self):
        return u"%s" % (self.name, )

class Country(HistoryMixin):
    # ISO3 code
    code = models.TextField(max_length=4, unique=True, db_index=True)
    numcode = models.IntegerField(unique=True, db_index=True)
    name = models.TextField(max_length=100, db_index=True)
    printable_name = models.TextField(max_length=100)
    
    def __unicode__(self):
        return u"%s" % (self.name, )

class State(HistoryMixin):
    code = models.TextField(max_length=4, db_index=True, blank=True, null=True)
    name = models.TextField(max_length=100, db_index=True, blank=True, null=True)
    country = models.ForeignKey("Country", to_field="code", blank=True, null=True, db_index=True)
    
    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.country)

    class Meta:
        unique_together = (("code", "country"))
    
class City(HistoryMixin):
    name = models.TextField(max_length=200, db_index=True)
    state = models.ForeignKey("State", blank=True, null=True, db_index=True)

    def __unicode__(self):
        return u"%s, %s" % (self.name, self.state)
    
class Artist(HistoryMixin, TaggedMixin):
    uid = models.IntegerField(unique=True, db_index=True)
    mbgid = models.TextField(max_length=48, blank=True)
    
    name = models.TextField(blank=True, db_index=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField()
    album_count = models.IntegerField(default=1)
    
    city = models.ForeignKey("City", blank=True, null=True, db_index=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=10, blank=True, null=True)
    longitude = models.DecimalField(max_digits=13, decimal_places=10, blank=True, default=True)
    
    def __unicode__(self):
        return u"%s" % (self.name, )

    def get_quoted_name(self):
        return urllib.quote(self.name)

    def get_mp3_m3u(self):
        url_tpl = "http://api.jamendo.com/get2/stream/album/m3u/?id=%s&streamencoding=mp31"
        album_ids = map(str, list(self.album_set.values_list("uid", flat=True)))
        album_ids_str = "+".join(album_ids)
        return url_tpl % album_ids_str

    def get_ogg_m3u(self):
        url_tpl = "http://api.jamendo.com/get2/stream/album/m3u/?id=%s&streamencoding=ogg2"
        album_ids = map(str, list(self.album_set.values_list("uid", flat=True)))
        album_ids_str = "+".join(album_ids)
        return url_tpl % album_ids_str

class Track(HistoryMixin, TaggedMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)
    mbgid = models.TextField(max_length=48, blank=True)

    name = models.TextField(blank=True, db_index=True)
    url = models.URLField()
    duration = models.IntegerField(default=0)
    album = models.ForeignKey("Album")
    artist = models.ForeignKey("Artist")
    numalbum = models.IntegerField(default=1)
    
    filename = models.TextField()
    genre = models.ForeignKey("Genre", null=True)
    license = models.ForeignKey("License", null=True)

    def __unicode__(self):
        return u"%s - %s (%s)" % (self.name, self.album, self.artist)

    def get_human_duration(self):
        return u"%d:%.2d" % (self.duration / 60, self.duration % 60)

    def get_mp3_url(self):
        return "http://api.jamendo.com/get2/stream/track/m3u/?id=%d&streamencoding=mp31" % self.uid
    
    def get_ogg_url(self):
        return "http://api.jamendo.com/get2/stream/track/m3u/?id=%d&streamencoding=ogg2" % self.uid
    
class Playlist(HistoryMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)
    name = models.TextField(blank=True, db_index=True)
    duration = models.IntegerField(default=0)

    def __unicode__(self):
        return u"%s (%d)" % (self.name, self.duration)

class Language(HistoryMixin):
    code = models.TextField(max_length=2, unique=True, db_index=True)
    name = models.TextField(blank=True, db_index=True)

class JamendoUser(HistoryMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)

    name = models.TextField(blank=True, db_index=True)
    idstr = models.TextField(unique=True, db_index=True)
    image = models.URLField(blank=True, null=True)
    language = models.ForeignKey("Language", to_field="code")

    def __unicode__(self):
        return u"%s" % self.name

class Review(HistoryMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)

    name = models.TextField(blank=True, db_index=True)
    text = models.TextField()
    rating = models.IntegerField(max_length=2, default=0)
    language = models.ForeignKey("Language", to_field="code")
    
    def __unicode__(self):
        return u"%s (%d)" % (self.name, self.language)

class Radio(HistoryMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)
    
    idstr = models.TextField(unique=True, db_index=True)
    name = models.TextField(blank=True, db_index=True)
    duration = models.IntegerField(default=0)
    weight = models.IntegerField(default=1)
    image = models.URLField(blank=True, null=True)

