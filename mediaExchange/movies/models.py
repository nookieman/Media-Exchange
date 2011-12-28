from django.db import models
from django.contrib.auth.models import User


class DownloadFile(models.Model):
    item = models.ForeignKey('Item')
    downloadLink = models.URLField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return "<DownloadFile %s (%s)" % (str(self.item), str(self.downloadLink))

class Item(models.Model):
    name = models.CharField(max_length=256)
    path = models.CharField(max_length=1024)
    size = models.IntegerField()
    mtime = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.name

class Language(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

class MovieGenre(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

class MovieSource(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Movie(Item):
    subname = models.CharField(max_length=256, blank=True, null=True)
    language = models.ForeignKey('Language', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey('MovieGenre', blank=True, null=True)
    source = models.ForeignKey('MovieSource', blank=True, null=True)

    def __unicode__(self):
        return self.name

class UploadRequest(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey('Item')
    state = models.IntegerField(default=0)
    tries = models.IntegerField(default=0)
    done = models.BooleanField(default=False)
    tared = models.IntegerField(default=0)
    encrypted = models.IntegerField(default=0)
    splitted = models.IntegerField(default=0)
    uploaded = models.IntegerField(default=0)

    def __unicode__(self):
        return 'UploadRequest: %s %s' % (self.item, 'done' if self.done else 'not done')

class Vote(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey('Item')
    watchable = models.BooleanField()
