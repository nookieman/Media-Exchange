import os.path

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
    itemInstance = models.ForeignKey('ItemInstance')
    key = models.ForeignKey('EncryptionKey', blank=False, null=False)

    def getDownloadFiles(self):
        return DownloadFile.objects.filter(downloadFileGroup=self.id)

    def __unicode__(self):
        return "<DownloadFileGroup %s>" % str(self.itemInstance)

class DownloadFile(models.Model):
    downloadFileGroup = models.ForeignKey('DownloadFileGroup')
    downloadLink = models.URLField(max_length=1024, blank=True, null=True)

    def __unicode__(self):
        return "<DownloadFile %s (%s)" % (str(self.downloadFileGroup.itemInstance), str(self.downloadLink))

class Item(models.Model):
    name = models.CharField(max_length=256)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.getRealModel().__unicode__()

    def getName(self):
        return self.name

    def getRealModel(self):
        realModel = None
        try:
            realModel = Movie.objects.get(id=self.id)
        except Movie.DoesNotExist:
            try:
                realModel = Season.objects.get(id=self.id)
            except Season.DoesNotExist:
                try:
                    realModel = Audio.objects.get(id=self.id)
                except Audio.DoesNotExist:
                    raise Exception("ERROR: Item not identifiable")
        return realModel

    def toDict(self):
        realModel = self.getRealModel()
        return realModel.toDict()

    @staticmethod
    def fromDict(struct):
        keys = {}
        if struct.has_key('keys'):
            for keyid, keyvals in struct['keys'].items():
                keys[keyid] = EncryptionKey.getOrCreate(chunkSize=keyvals['chunkSize'],
                                                        keydata=keyvals['key'])

        if struct.has_key('movies'):
            for moviestruct in struct['movies']:
                genre = Genre.getOrCreate(moviestruct.get('genre', None))
                movie = Movie.getOrCreate(name=moviestruct.get('name'),
                                          subname=moviestruct.get('subname', None),
                                          year=moviestruct.get('year', None),
                                          genre=genre)
                Item._createDownloadFileGroups(moviestruct.get('downloadFileGroups', []),
                                               movie, keys)

        if struct.has_key('series'):
            for seriestruct in struct['series']:
                genre = Genre.getOrCreate(seriestruct.get('genre', None))
                serie = Serie.getOrCreate(seriestruct['name'])
                season = Season.getOrCreate(serie=serie,
                                            number=seriestruct['number'],
                                            subname=seriestruct.get('subname', None),
                                            year=seriestruct.get('year', None),
                                            genre=genre)
                Item._createDownloadFileGroups(seriestruct.get('downloadFileGroups', []),
                                               seasonInstance, keys)

    @staticmethod
    def _createDownloadFileGroups(struct, item, keys):
        for downloadFileGroup in struct:
            lang = Language.getOrCreate(downloadFileGroup.get('language', None))
            source = Source.getOrCreate(downloadFileGroup.get('source', None))
            itemInstance = ItemInstance.getOrCreate(item=item,
                                                    language=lang,
                                                    source=source,
                                                    size=downloadFileGroup.get('size', None))
            key = keys[downloadFileGroup['key']]
            dfg = DownloadFileGroup(itemInstance=itemInstance, key=key)
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

class ItemInstance(models.Model):
    creator = models.ForeignKey(User, blank=True, null=True)
    item = models.ForeignKey('Item')
    language = models.ForeignKey('Language', blank=True, null=True)
    source = models.ForeignKey('Source', blank=True, null=True)
    path = models.CharField(max_length=1024, blank=True, null=True)
    present = models.BooleanField(default=False)
    size = models.IntegerField(blank=True, null=True)
    mtime = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "<ItemInstance '%s' in '%s;%s'>" % (str(self.item), str(self.language), str(self.source))

    def getDownloadFileGroups(self):
        return DownloadFileGroup.objects.filter(itemInstance=self)

    def getUploadRequest(self):
        uploadRequest = None
        try:
            uploadRequest = UploadRequest.objects.filter(itemInstance=self)
        except UploadRequest.DoesNotExist:
            pass
        return uploadRequest

    def isPathAvailable(self):
        return self.path != None and os.path.exists(self.path)

    def getSizeString(self):
        sizeString = "Unknown"
        size = self.size
        if size:
            s = (size, 'byte')
            if size > 1073741824:
                s = (round(size/1073741824.0, 2), 'GB')
            elif size > 1048576:
                s = (round(size/1048576.0, 2), 'MB')
            elif size > 1024:
                s = (round(size/1024.0, 2), 'KB')
            sizeString = "%.2f %s" % s
        return sizeString


    def toDict(self):
        d = {}
        if self.language:
            d['language'] = self.language.name
        if self.source:
            d['source'] = self.source.name
        if self.size:
            d['size'] = self.size
        return d

    def getRequestMailSubject(self, requester):
        realItem = self.item.getRealModel()
        category = realItem.getTypeString()
        subject = "%s <%s> has request a %s" % (requester.username,
                                                requester.email,
                                                category)
        return subject

    def getRequestMailBody(self, requester):
        realItem = self.item.getRealModel()
        category = realItem.getTypeString()
        itemRequestString = realItem.getItemRequestString()
        body = "%s <%s> has request the '%s' %s'" % (requester.username,
                                                     requester.email,
                                                     category,
                                                     itemRequestString)
        if self.language:
            body += " in %s" % self.language.name
        if self.source:
            body += " source: '%s'" % self.source.name
        return body

    @staticmethod
    def getOrCreate(item, language=None, source=None, size=None, creator=None):
        itemInstance = ItemInstance.objects.filter(item=item, language=language,
                                                   source=source, size=size,
                                                   creator=creator)
        if len(itemInstance) > 0:
            itemInstance = itemInstance[0]
        else:
            itemInstance = ItemInstance(item=item, language=language,
                                        source=source, size=size,
                                        creator=creator)
            itemInstance.save()
        return itemInstance


class ItemRequest(models.Model):
    requester = models.ForeignKey(User)
    itemInstance = models.ForeignKey('ItemInstance')
    processed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s (%s)" % (str(self.requester),
                               str(self.itemInstance),
                               "processed" if self.processed else "not processed")

class UploadRequest(models.Model):
    user = models.ForeignKey(User)
    itemInstance = models.ForeignKey('ItemInstance')
    state = models.IntegerField(default=0)
    tries = models.IntegerField(default=0)
    done = models.BooleanField(default=False)
    tared = models.IntegerField(default=0)
    encrypted = models.IntegerField(default=0)
    splitted = models.IntegerField(default=0)
    uploaded = models.IntegerField(default=0)

    def __unicode__(self):
        return 'UploadRequest: %s %s' % (self.itemInstance, 'done' if self.done else 'not done')

class Comment(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey('Item')
    subject = models.CharField(max_length=256)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "<Comment from '%s' on '%s': '%s'>" % (self.user.username, str(self.item), self.subject)

class Rating(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey('Item')
    rating = models.IntegerField(choices=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)))
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return "<Rating from '%s' on '%s': '%d'>" % (self.user.username, str(self.item), self.rating)

    @staticmethod
    def updateOrCreate(user, item, rating):
        rating = None
        try:
            rating = Rating.objects.get(item=item, user=user)
            rating.rating = rating
        except Rating.DoesNotExist:
            rating = Rating(user=user, item=item, rating=rating)
        rating.save()

class Movie(Item):
    subname = models.CharField(max_length=256, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey('Genre', blank=True, null=True)

    def __unicode__(self):
        return self.name

    def getName(self):
        return "%s" % self.name

    def getSubname(self):
        return self.subname

    def getTypeString(self):
        return "movie"

    def getItemRequestString(self):
        request = "'%s'" % (self.name)
        if self.subname:
            request += " (%s)" % self.subname
        return request

    @staticmethod
    def exists(name, subname, year, genre):
        return Movie.objects.filter(name=name, subname=subname, year=year, genre=genre).count() > 0

    @staticmethod
    def getOrCreate(name, subname=None, year=None, genre=None, size=None):
        movie = Movie.objects.filter(name=name, subname=subname, year=year, genre=genre)
        if len(movie) > 0:
            movie = movie[0]
        else:
            movie = Movie(name=name, subname=subname, year=year, genre=genre)
            movie.save()
        return movie

    def toDict(self):
        d = {'id'   : self.id,
             'name' : self.name}
        if self.subname:
            d.update({'subname' : self.subname})
        if self.year:
            d.update({'year' : self.year})
        if self.genre:
            d.update({'genre' : self.genre.name})
        return d

class Serie(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    @staticmethod
    def getOrCreate(name):
        serie = Serie.objects.filter(name=name)
        if len(serie) > 0:
            serie = serie[0]
        else:
            serie = Serie(name=name)
            serie.save()
        return serie

class Season(Item):
    serie = models.ForeignKey('Serie')
    subname = models.CharField(max_length=256, blank=True, null=True)
    number = models.IntegerField(blank=False, null=False)
    genre = models.ForeignKey('Genre', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    directoryListing = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s S%d" % (self.serie.name, self.number)

    def getName(self):
        return "%s" % self.serie.name

    def getSubname(self):
        subname = "season %d" % self.number
        if self.subname:
            subname += " (%s)" % self.subname
        return subname

    def getTypeString(self):
        return "serie"

    def getItemRequestString(self):
        request = "'%s' season %d" % (self.series.name, self.number)
        if self.subname:
            request += " (%s)" % self.subname
        return request

    @staticmethod
    def getOrCreate(serie, number, subname=None, genre=None, year=None):
        season = Season.objects.filter(serie=serie, subname=subname, number=number, genre=genre, year=year)
        if len(season) > 0:
            season = season[0]
        else:
            season = Season(serie=serie, subname=subname, number=number, genre=genre, year=year)
            season.save()
        return season

    def toDict(self):
        d = {'id'     : self.id,
             'name'   : self.serie.name,
             'number' : self.number}
        if self.subname:
            d['subname'] = self.subname
        if self.year:
            d['year'] = self.year
        if self.genre:
            d['genre'] = self.genre.name
        return d

class Artist(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

    @staticmethod
    def getOrCreate(name):
        try:
           artist = Artist.objects.get(name=name)
        except Artist.DoesNotExist:
            artist = Artist(name=name)
            artist.save()
        return artist

class Audio(Item):
    artist = models.ForeignKey('Artist', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genre = models.ForeignKey('Genre', blank=True, null=True)

    def __unicode__(self):
        uc = self.getName()
        if self.year:
            uc += " (%d)" % self.year
        return uc

    def toDict(self):
        d = {'id'     : self.id,
             'name'   : self.name}
        if self.artist:
            d['artist'] = self.artist.name
        if self.year:
            d['year'] = self.year
        if self.genre:
            d['genre'] = self.genre.name
        return d

    def getName(self):
        uc = ""
        if self.artist:
            uc = "%s - " % self.artist
        uc += self.name
        return uc

    def getSubname(self):
        return None

    def getTypeString(self):
        return "audio"

    def getItemRequestString(self):
        return self.__unicode__()

    @staticmethod
    def getOrCreate(name, artist=None, genre=None, year=None):
        try:
           audio = Audio.objects.get(name=name, artist=artist, genre=genre, year=year)
        except Audio.DoesNotExist:
            audio = Audio(name=name, artist=artist, genre=genre, year=year)
            audio.save()
        return audio

class Vote(models.Model):

    user = models.ForeignKey(User)
    item = models.ForeignKey('Item')
    watchable = models.BooleanField()
