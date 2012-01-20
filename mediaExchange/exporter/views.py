import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFileGroup, DownloadFile, EncryptionKey, ItemInstance
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
                      'subname' : ...
                      'genre'  : ...,
                      'instance' : [ {
                                      'size' : ...,
                                      'language' : ...,
                                      'source' : ...,
                                      'downloadFileGroups' : [{
                                                               'downloadLinks': [...],
                                                               'key': ...
                                                             }, ...],
                                   }, ... ],
                   }, ...],
        'series' : [ {
                      'id' : ...,
                      'name' : ...,
                      'number' : ...,
                      'subname' : ...,
                      'genre'  : ...,
                      'instance' : [ {
                                      'size' : ...,
                                      'language' : ...,
                                      'source' : ...,
                                      'downloadFileGroups' : [{
                                                               'downloadLinks': [...],
                                                               'key': ...
                                                             }, ...],
                                   }, ... ],
                   }, ...]
    }
    """
    jsonStruct = createExportStruct(movies=Movie.objects.all(),
                                    seasons=Season.objects.all(),
                                    onlyDownloadable=True)
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

@login_required
def exporterexportall(request):
    jsonStruct = createExportStruct(movies=Movie.objects.all(),
                                    seasons=Season.objects.all())
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

def _jsonStructFromItemList(items, onlyDownloadable=False):
    itemStruct = []
    for item in items:
        itemDict = item.toDict()
        instancesList = []
        for instance in ItemInstance.objects.filter(item=item):
            instanceDict = instance.toDict()
            downloadFileGroupsList = []
            for downloadFileGroup in DownloadFileGroup.objects.filter(itemInstance=instance):
                downloadFiles = DownloadFile.objects.filter(downloadFileGroup=downloadFileGroup)
                downloadLinks = []
                for downloadFile in downloadFiles:
                    downloadLinks.append(downloadFile.downloadLink)
                downloadFileGroupsList.append({'downloadLinks' : downloadLinks,
                                               'key'           : downloadFileGroup.key.id})
            instanceDict['downloadFileGroups'] = downloadFileGroupsList
            instancesList.append(instanceDict)
        itemDict['instances'] = instancesList
        itemStruct.append(itemDict)
    return itemStruct

def createExportStruct(movies, seasons, onlyDownloadable=False):
    jsonStruct = {}
    jsonStruct['movies'] = _jsonStructFromItemList(items=movies)
    jsonStruct['series'] = _jsonStructFromItemList(items=seasons)
    jsonStruct['keys'] = _jsonStructKeys()
    return jsonStruct

def _jsonStructKeys(keyIdList=None):
    keysStruct = {}
    for key in EncryptionKey.objects.all():
        if not keyIdList or key.id in keyIdList:
            keysStruct[key.id] = {'chunkSize' : key.chunkSize,
                                  'key'       : key.key}
    return keysStruct

