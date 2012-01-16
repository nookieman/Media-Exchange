import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFileGroup, DownloadFile, EncryptionKey
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
                        'downloadFileGroups' : [{'downloadLinks': [...], 'key': ...}, ...],
                     }, ...]
    }
    """
    jsonStruct = {}
    jsonStruct['movies'] = _jsonStructFromItemList(items=Movie.objects.all(),
                                                   onlyDownloadable=True)
    jsonStruct['series'] = _jsonStructFromItemList(items=Season.objects.all(),
                                                   onlyDownloadable=True)
    jsonStruct['keys'] = _jsonStructKeys()
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

@login_required
def exporterexportall(request):
    jsonStruct = {}
    jsonStruct['movies'] = _jsonStructFromItemList(items=Movie.objects.all())
    jsonStruct['series'] = _jsonStructFromItemList(items=Season.objects.all())
    jsonStruct['keys'] = _jsonStructKeys()
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

def _jsonStructFromItemList(items, onlyDownloadable=False):
    itemStruct = []
    for item in items:
        itemDict = item.toDict()
        downloadFileGroups = DownloadFileGroup.objects.filter(item=item)
        if downloadFileGroups:
            itemDict['downloadFileGroups'] = []
            for downloadFileGroup in downloadFileGroups:
                downloadFiles = DownloadFile.objects.filter(downloadFileGroup=downloadFileGroup)
                downloadLinks = []
                for downloadFile in downloadFiles:
                    downloadLinks.append(downloadFile.downloadLink)
                itemDict['downloadFileGroups'].append({'downloadLinks' : downloadLinks,
                                                       'key'           : downloadFileGroup.key.id})
        itemStruct.append(itemDict)
    return itemStruct

def _jsonStructKeys():
    keysStruct = {}
    for key in EncryptionKey.objects.all():
        keysStruct[key.id] = {'chunkSize' : key.chunkSize,
                              'key'       : key.key}
    return keysStruct

