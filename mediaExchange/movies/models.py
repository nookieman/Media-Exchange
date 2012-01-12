from django.db import models
from django.contrib.auth.models import User


class EncryptionKey(models.Model):
    chunkSize = models.IntegerField(blank=False, null=False)
    key = models.TextField(blank=False, null=False)

    @staticmethod
    def fromFileHandle(fileHandle):
        chunkSize = int(fileHandle.readline())
        keydata = fileHandle.read()
        return EncryptionKey.getOrCreate(chunkSize, keydata)


    @staticmethod
    def getOrCreate(chunkSize, keydata):
        key = None
        try:
            key = EncryptionKey.objects.get(chunkSize=chunkSize, key=keydata)
        except EncryptionKey.DoesNotExist, e:
            key = EncryptionKey(chunkSize=chunkSize, key=keydata)
            key.save()
        return key


class DownloadFile(models.Model):
    item = models.ForeignKey('Item')
    downloadLink = models.URLField(max_length=1024, blank=True, null=True)
    key = models.ForeignKey('EncryptionKey', blank=False, null=False)

    def __unicode__(self):
        return "<DownloadFile %s (%s)" % (str(self.item), str(self.downloadLink))

class Item(models.Model):
    creator = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=256)
    path = models.CharField(max_length=1024, blank=True, null=True)
    present = models.BooleanField(default=False)
    size = models.IntegerField(blank=True, null=True)
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

    def toDict(self):
        d = {'id'   : self.id,
             'name' : self.name,
             'size' : self.size}
        if self.subname:
            d.update({'subname' : self.subname})
        if self.language:
            d.update({'language' : self.language.name})
        if self.year:
            d.update({'year' : self.year})
        if self.genre:
            d.update({'genre' : self.genre.name})
        if self.source:
            d.update({'source' : self.source.name})
        return d

class ItemRequest(models.Model):
    requester = models.ForeignKey(User)
    item = models.ForeignKey('Item')
    processed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s (%s)" % (str(self.requester),
                               str(self.item),
                               "processed" if self.processed else "not processed")

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
