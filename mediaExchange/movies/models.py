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

class DownloadFileGroup(models.Model):
    item = models.ForeignKey('Item')
    key = models.ForeignKey('EncryptionKey', blank=False, null=False)

    def getDownloadFiles(self):
        return DownloadFile.objects.filter(downloadFileGroup=self.id)

    def __unicode__(self):
        return "<DownloadFileGroup %s>" % str(self.item)

class DownloadFile(models.Model):
    downloadFileGroup = models.ForeignKey('DownloadFileGroup')
    downloadLink = models.URLField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return "<DownloadFile %s (%s)" % (str(self.downloadFileGroup.item), str(self.downloadLink))

class Item(models.Model):
    creator = models.ForeignKey(User, blank=True, null=True)
    name = models.CharField(max_length=256)
    path = models.CharField(max_length=1024, blank=True, null=True)
    present = models.BooleanField(default=False)
    size = models.IntegerField(blank=True, null=True)
    mtime = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "<Item %s by %s>" % (self.name, str(self.creator))

    @staticmethod
    def fromDict(struct):

        keys = {}
        if struct.has_key('keys'):
            for keyid, keyvals in struct['keys'].items():
                keys[keyid] = EncryptionKey.getOrCreate(chunkSize=keyvals['chunkSize'],
                                                        keydata=keyvals['key'])

        if struct.has_key('movies'):
            for moviestruct in struct['movies']:
                lang = Language.getOrCreate(moviestruct.get('language', None))
                genre = Genre.getOrCreate(moviestruct.get('genre', None))
                source = Source.getOrCreate(moviestruct.get('source', None))
                movie = Movie.getOrCreate(name=moviestruct.get('name'),
                                          size=moviestruct.get('size', None),
                                          subname=moviestruct.get('subname', None),
                                          year=moviestruct.get('year', None),
                                          language=lang,
                                          genre=genre,
                                          source=source)
                Item._createDownloadFileGroups(moviestruct.get('downloadFileGroups', []), keys)

        if struct.has_key('series'):
            from mediaExchange.series.models import Serie, Season
            for seriestruct in struct['series']:
                lang = Language.getOrCreate(seriestruct.get('language', None))
                genre = Genre.getOrCreate(seriestruct.get('genre', None))
                source = Source.getOrCreate(seriestruct.get('source', None))
                serie = Serie.getOrCreate(seriestruct['name'])
                season = Season.getOrCreate(serie=serie,
                                            number=seriestruct['number'],
                                            size=seriestruct.get('size', None),
                                            subname=seriestruct.get('subname', None),
                                            year=seriestruct.get('year', None),
                                            language=lang,
                                            genre=genre,
                                            source=source)
                Item._createDownloadFileGroups(seriestruct.get('downloadFileGroups', []), keys)

    @staticmethod
    def _createDownloadFileGroups(struct, keys):
        for downloadFileGroup in struct:
            key = keys[downloadFileGroup['key']]
            dfg = DownloadFileGroup(item=season, key=key)
            dfg.save()
            for downloadLink in downloadFileGroup['downloadLinks']:
                df = DownloadFile(downloadFileGroup=dfg,
                                  downloadLink=downloadLink)
                df.save()




class Language(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def getOrCreate(name):
        lang = None
        if name:
            lang = Language.objects.filter(name=name)
            if len(lang) > 0:
                lang = lang[0]
            else:
                lang = Language(name=name)
                lang.save()
        return lang

class Genre(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def getOrCreate(name):
        genre = None
        if name:
            genre = Genre.objects.filter(name=name)
            if len(genre) > 0:
                genre = genre[0]
            else:
                genre = Genre(name=name)
                genre.save()
        return genre

class Source(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def getOrCreate(name):
        source = None
        if name:
            source = Source.objects.filter(name=name)
            if len(source) > 0:
                source = source[0]
            else:
                source = Source(name=name)
                source.save()
        return source

class Movie(Item):
    subname = models.CharField(max_length=256, blank=True, null=True)
    language = models.ForeignKey('Language', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey('Genre', blank=True, null=True)
    source = models.ForeignKey('Source', blank=True, null=True)

    def __unicode__(self):
        return self.name

    @staticmethod
    def exists(name, subname, language, year, genre, source):
        return Movie.objects.filter(name=name, subname=subname, language=language, year=year, genre=genre, source=source).count() > 0

    @staticmethod
    def getOrCreate(name, subname, language, year, genre, source, size=None):
        movie = Movie.objects.filter(name=name, subname=subname, language=language, year=year, genre=genre, source=source)
        if len(movie) > 0:
            movie = movie[0]
        else:
            movie = Movie(name=name, subname=subname, language=language, year=year, genre=genre, source=source)
            movie.save()
        return movie

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
