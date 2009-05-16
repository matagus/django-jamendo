#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        ordering = ["name"]
        verbose_name = "album"
        verbose_name_plural = "albums"

    def __unicode__(self):
        return u"%s - %s" % (self.name, self.artist)

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
    code = models.TextField(max_length=4, unique=True, db_index=True)
    name = models.TextField(max_length=100, db_index=True)

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
    
class TagInfo(HistoryMixin):
    uid = models.IntegerField(unique=True, null=True, blank=True)
    weight = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    tag = models.ForeignKey("tagging.Tag")

    def __unicode__(self):
        return u"%s (%d)" % (self.tag, self.weight)
    
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

