from django.db import models

from mediaExchange.movies.models import Item

class SerieGenre(models.Model): 
    name = models.CharField(max_length=256, blank=True, null=True) 
 
    def __unicode__(self): 
        return self.name 
 
class SerieSource(models.Model): 
    name = models.CharField(max_length=256, blank=True, null=True) 
 
    def __unicode__(self): 
        return self.name 

class Language(models.Model): 
    name = models.CharField(max_length=256, blank=True, null=True) 
 
    def __unicode__(self): 
        return self.name 

class Serie(models.Model):
    name = models.CharField(max_length=256)
    subname = models.CharField(max_length=256, blank=True, null=True)

    def __unicode__(self):
        return self.name

class Season(Item):
    serie = models.ForeignKey('Serie')
    language = models.ForeignKey('Language', blank=True, null=True)
    genre = models.ForeignKey('SerieGenre', blank=True, null=True)
    source = models.ForeignKey('SerieSource', blank=True, null=True)

    def __unicode__(self):
        return "%s - %s" % (self.serie.name, self.name)
