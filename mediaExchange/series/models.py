from django.db import models
from django.db.models import get_model

from mediaExchange.movies.models import Item, Language, Genre, Source

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
            serie = Serie(name)
            serie.save()
        return serie


class Season(Item):
    serie = models.ForeignKey('Serie')
    subname = models.CharField(max_length=256, blank=True, null=True)
    number = models.IntegerField(blank=False, null=False)
    language = models.ForeignKey(get_model('movies', 'Language'), blank=True, null=True)
    genre = models.ForeignKey(get_model('movies', 'Genre'), blank=True, null=True)
    source = models.ForeignKey(get_model('movies', 'Source'), blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    directoryListing = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return "%s S%d" % (self.serie.name, self.number)

    @staticmethod
    def getOrCreate(serie, subname, number, language, genre, source, year, size=None):
        season = Season.objects.filter(serie=serie, subname=subname, number=number, language=language, genre=genre, source=source, year=year)
        if len(season) > 0:
            season = season[0]
        else:
            season = Season(serie=serie, subname=subname, number=number, language=language, genre=genre, source=source, year=year)
            season.save()
        return season

    def toDict(self):
        d = {'id'     : self.id,
             'name'   : self.serie.name,
             'size'   : self.size,
             'number' : self.number}
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

# keep this if decide to make single episodes available
#class Episode(Item):
#    season = models.ForeignKey('Season')
#    number = models.IntegerField(blank=False, null=False)
#    title = models.CharField(max_length=256, blank=True, null=True)
#
#    def __unicode__(self):
#        return "%s S%dE%d" % (self.season.serie.name, self.season.number, self.number)
