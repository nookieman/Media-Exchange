from django.db import models
from django.db.models import get_model

from mediaExchange.movies.models import Item, Language

class SerieGenre(models.Model): 
    name = models.CharField(max_length=256, blank=True, null=True) 
 
    def __unicode__(self): 
        return self.name 
 
class SerieSource(models.Model): 
    name = models.CharField(max_length=256, blank=True, null=True) 
 
    def __unicode__(self): 
        return self.name 

class Serie(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class Season(Item):
    serie = models.ForeignKey('Serie')
    subname = models.CharField(max_length=256, blank=True, null=True)
    number = models.IntegerField(blank=False, null=False)
    language = models.ForeignKey(get_model('movies', 'Language'), blank=True, null=True)
    genre = models.ForeignKey('SerieGenre', blank=True, null=True)
    source = models.ForeignKey('SerieSource', blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return "%s S%d" % (self.serie.name, self.number)

# keep this if decide to make single episodes available
#class Episode(Item):
#    season = models.ForeignKey('Season')
#    number = models.IntegerField(blank=False, null=False)
#    title = models.CharField(max_length=256, blank=True, null=True)
#
#    def __unicode__(self):
#        return "%s S%dE%d" % (self.season.serie.name, self.season.number, self.number)
