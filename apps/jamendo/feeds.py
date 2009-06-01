# -*- coding: utf-8 -*-

from datetime import datetime

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from atom import Feed
from tagging.models import Tag
from jamendo.models import Artist, Album


ITEMS_PER_FEED = getattr(settings, 'ITEMS_PER_FEED', 20)


class BaseFeed(Feed):
    def __init__(self, *args, **kwargs):
        super(BaseFeed, self).__init__(args, kwargs)
        self.site = Site.objects.get(pk=settings.SITE_ID)

    def _get_qs(self):
        raise NotImplementedError
    
    def item_title(self, item):
        return unicode(item)

    def item_updated(self, item):
        return item.modified_at
    
    def item_published(self, item):
        return item.added_at

    def item_authors(self, item):
        return [{"name" : item.name}]

    def feed_updated(self):
        try:
            updated_at = self._get_qs().latest("modified_at").modified_at
        except AttributeError:
            # We return an arbitrary date if there are no results, because there
            # must be a feed_updated field as per the Atom specifications, however
            # there is no real data to go by, and an arbitrary date can be static.
            return datetime(year=2009, month=1, day=1)

    def items(self):
        return self._get_qs().all().order_by("-added_at")[:ITEMS_PER_FEED]

    #def feed_icon(self, obj):
        # return URI
    
    #def feed_logo(self, obj):
        # return URI

class ArtistsFeed(BaseFeed):
    def __init__(self, *args, **kwargs):
        super(ArtistsFeed, self).__init__(args, kwargs)

    def _get_qs(self):
        return Artist.objects

    def item_id(self, item):
        return "http://%s%s" % (self.site.domain, reverse("jamendo_artist", args=(item.pk,)))

    def item_guid(self, item):
        return reverse("jamendo_artist", args=(item.pk,))
    
    def item_content(self, item):
        return {"type": "html", "xml:base": "http://%s" % self.site.domain},\
            render_to_string('jamendo/artists/feed.html', {"instance": item})
    
    def item_links(self, item):
        return [{"href" : "http://%s%s" % (self.site.domain, reverse("jamendo_artist", args=(item.pk,)))}]
    
    def feed_id(self):
        return "http://%s/feeds/artists/" % (self.site.domain,)

    def feed_guid(self):
        return reverse("jamendo_artists")

    def feed_links(self):
        return ({"type": "text/html", "rel": "self",
            "href": "http://%s%s" % (self.site.domain, reverse('jamendo_artists'))},
            {"rel": "alternate", "type": "text/html", "href": "http://www.jamendo.com/en/artists/"},)

    def feed_title(self):
        return _("Artists in %s") % self.site.name

    def feed_subtitle(self):
        return _("Artists recently added to Jamendo.com")

    def item_categories(self, item):
        return [{"term": tag.name} for tag in item.tags]

class AlbumsFeed(BaseFeed):
    def __init__(self, *args, **kwargs):
        super(AlbumsFeed, self).__init__(args, kwargs)
    
    def _get_qs(self):
        return Album.objects
    
    def item_id(self, item):
        return "http://%s%s" % (self.site.domain, reverse("jamendo_album", args=(item.pk,)))

    def item_guid(self, item):
        return reverse("jamendo_album", args=(item.pk,))
    
    def item_content(self, item):
        return {"type": "html", "xml:base": "http://%s" % self.site.domain},\
            render_to_string('jamendo/albums/feed.html', {"instance": item})
    
    def item_links(self, item):
        return [{"href" : "http://%s%s" % (self.site.domain, reverse("jamendo_album", args=(item.pk,)))},
                {"href": item.get_mp3_url(), "rel": "enclosure", "type": "audio/mpeg"}]

    def feed_guid(self):
        return reverse("jamendo_albums")
    
    def feed_id(self):
        return "%sfeeds/albums/" % (self.site.domain,)
    
    def feed_links(self):
        return ({"type": "text/html", "rel": "self",
            "href": "http://%s%s" % (self.site.domain, reverse('jamendo_albums'))},
            {"rel": "alternate", "type": "text/html", "href": "http://www.jamendo.com/en/albums/"},)

    def feed_title(self):
        return _("Albums in %s") % self.site.name

    def feed_subtitle(self):
        return _("Albums recently added to Jamendo.com")

class AlbumsForFeed(BaseFeed):
    """
    Feed of albums for a given artist
    """
    def __init__(self, *args, **kwargs):
        super(AlbumsForFeed, self).__init__(args, kwargs)

    def get_object(self, bits):
        if bits:
            artist = Artist.objects.get(pk=bits[0])
            self.artist = artist
            return artist
        return None
    
    def _get_qs(self):
        return Artist.objects

    def items(self):
        return self.artist.album_set.all().order_by("name")

    def item_id(self, item):
        return "http://%s%s" % (self.site.domain, reverse("jamendo_album", args=(item.pk,)))

    def item_guid(self, item):
        return reverse("jamendo_album", args=(item.pk,))
    
    def item_content(self, item):
        return {"type": "html", "xml:base": "http://%s" % self.site.domain},\
            render_to_string('jamendo/albums/feed.html', {"instance": item})
    
    def item_links(self, item):
        return [{"href" : "http://%s%s" % (self.site.domain, reverse("jamendo_album", args=(item.pk,)))}]
    
    def feed_id(self, item):
        return "http://%s/feeds/albumsfor/%d/" % (self.site.domain, item.pk)

    def feed_guid(self):
        return reverse("jamendo_artist", args=(item.pk,))

    def feed_links(self):
        return ({"type": "text/html", "rel": "self",
            "href": "http://%s%s" % (self.site.domain, reverse('jamendo_artists'))},
            {"rel": "alternate", "type": "text/html", "href": "http://www.jamendo.com/en/artists/"},)

    def feed_title(self):
        return _("%s: albums in %s") % (self.artist.name, self.site.name)

    def feed_subtitle(self):
        return _("List of all its albums in Jamendo.com")

    def item_categories(self, item):
        return [{"term": tag.name} for tag in item.tags]

# TODO: feeds for:
# artists for a given country
# albums for a given license
# artists for a given tag