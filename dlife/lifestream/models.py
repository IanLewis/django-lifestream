#!/usr/bin/env python
#:coding=utf-8:
#:tabSize=2:indentSize=2:noTabs=true:
#:folding=explicit:collapseFolds=1:

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

class Lifestream(models.Model):
  '''A lifestream itself.'''
  ls_title = models.CharField(max_length=128)
  ls_tagline = models.TextField(null=True, blank=True)
  
  ls_baseurl = models.CharField(max_length=1000)
  
  ls_user = models.ForeignKey(User)
  
  def __unicode__(self):
    return self.ls_title
  
  class Meta:
    db_table="lifestream"

class FeedManager(models.Manager):
  ''' Query only normal feeds. '''
  
  def get_fetchable_feeds(self):
    return super(FeedManager, self) \
           .get_query_set().filter(feed_basic_feed=False, feed_fetchable=True)

class Feed(models.Model):
  '''A feed for gathering data.'''
  feed_lifestream = models.ForeignKey(Lifestream)
  
  feed_name = models.CharField(max_length=255)
  feed_url = models.URLField(verify_exists=True, max_length=1000)
  feed_domain = models.CharField(max_length=255)
  feed_fetchable = models.BooleanField(default=True)
  
  # Used for feeds that allow users to directly add to the lifestream.
  feed_basic_feed = models.BooleanField(default=False)
  
  objects = FeedManager()
  
  def __unicode__(self):
    return self.feed_name
    
  class Meta:
    db_table="feeds"

class Tag(models.Model):
  '''item tag'''
  tag_slug = models.SlugField(primary_key=True)
  tag_name = models.CharField(max_length=30)
  tag_count = models.IntegerField()
  
  tag_deleted = models.BooleanField(default=False)
  
  def __unicode__(self):
    return self.tag_name
  
  class Meta:
    db_table="tags"
    ordering=["-tag_count"]

class Item(models.Model):
  '''A feed item'''
  item_feed = models.ForeignKey(Feed)
  item_date = models.DateTimeField()
  item_title = models.CharField(max_length=255)
  item_content = models.TextField(null=True, blank=True)
  item_content_type = models.CharField(max_length=255, null=True, blank=True)
  item_clean_content = models.TextField(null=True, blank=True)
  item_author = models.CharField(max_length=255, null=True, blank=True)
  item_permalink = models.CharField(max_length=1000)
  
  #Tag string used to save tags using django-tagging
  item_tags = models.ManyToManyField(Tag, null=True, blank=True, db_table="item_tags")
  
  item_published = models.BooleanField(default=True)
  item_deleted = models.BooleanField(default=False)
  
  def _get_item_link(self):
    return self.item_feed.feed_lifestream.ls_baseurl + "item/" + str(self.id)
  
  item_link = property(_get_item_link)
  
  def __unicode__(self):
    return self.item_title
    
  class Meta:
    db_table="items"
    ordering=["-item_date", "item_feed"]