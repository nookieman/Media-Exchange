import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFile, EncryptionKey
from mediaExchange.series.models import Season

@login_required
def exporterexport(request):
    """
    This exports the already uploaded items in json format including the needed keys in json format:
    format: 
    {
        'keys' : {'1' : {'chunkSize' : ..., 'key' : ...}, ... },
        'movies' : [ {
                        'id' : ...,
                        'name' : ...,
                        'size' : ...,
                        'subname' : ...
                        'language' : ...,
                        'genre'  : ...,
                        'source' : ...,
                        ''}, ...],
        'series' : [ {
                        'id' : ...,
                        'name' : ...,
                        'size' : ...,
                        'number' : ...,
                        'subname' : ...,
                        'language' : ...,
                        'genre'  : ...,
                        'source' : ...,
                        'downloadFiles' : [{'downloadLink': ..., 'key': ...}, ...],
                     }, ...]
    }
    """
    movies = []
    seasons = []
    uploadRequests = UploadRequest.objects.filter(done=True)
    for uploadRequest in uploadRequests:
        id = uploadRequest.item.id
        try:
            movie = Movie.objects.get(id=id)
            movies.append(movie)
        except Movie.DoesNotExist, e:
            try:
                season = Season.objects.get(id=id)
                seasons.append(season)
            except Season.DoesNotExist, e:
                print "ERROR: item that is neither Movie nor Season"
    jsonStruct = {}
    jsonStruct['movies'] = _jsonStructFromItemList(movies)
    jsonStruct['series'] = _jsonStructFromItemList(seasons)
    jsonStruct['keys'] = _jsonStructKeys()
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

def _jsonStructFromItemList(items):
    itemStruct = []
    for item in items:
        downloadFiles = DownloadFile.objects.filter(item=item)
        if downloadFiles:
            itemDict = item.toDict()
            itemDict['downloadFiles'] = []
            for downloadFile in downloadFiles:
                itemDict['downloadFiles'].append({'downloadLink' : downloadFile.downloadLink,
                                                   'key'          : downloadFile.key.id})
            itemStruct.append(itemDict)
    return itemStruct

def _jsonStructFromSeasonList(seasons):
    seasonsStruct = []
    for season in seasons:
        downloadFiles = DownloadFile.objects.filter(item=season)
        if downloadFiles:
            seasonDict = season.toDict()
            seasonDict['downloadFiles'] = []
            for downloadFile in downloadFiles:
                seasonDict['downloadFiles'].append({'downloadLink' : downloadFile.downloadLink,
                                                    'key'          : downloadFile.key.id})
            seasonsStruct.append(seasonDict)

def _jsonStructKeys():
    keysStruct = {}
    for key in EncryptionKey.objects.all():
        keysStruct[key.id] = {'chunkSize' : key.chunkSize,
                              'key'       : key.key}
    return keysStruct


@login_required
def exporterexportall(request):
    jsonStruct = {}
    jsonStruct['movies'] = _jsonStructFromItemList(Movie.objects.all())
    jsonStruct['series'] = _jsonStructFromItemList(Season.objects.all())
    jsonStruct['keys'] = _jsonStructKeys()
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")
