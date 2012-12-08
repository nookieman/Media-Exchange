import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from mediaExchange.items.models import UploadRequest, DownloadFileGroup, DownloadFile, EncryptionKey, ItemInstance, Movie, Season, Audio

@login_required
def exporterexport(request):
    """
    This exports the already uploaded items in json format including the needed keys in json format:
    format:
    {
        'keys' : {'1' : {'chunkSize' : ..., 'key' : ...}, ... },
        'users' : {'1' : {'username' : ..., 'email' : ...}, ...},
        'movies' : [ {
                      'id' : ...,
                      'name' : ...,
                      'subname' : ...
                      'genres'  : [...],
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
                      'genres'  : [...],
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
        'audios' : [ {
                      'id' : ...,
                      'name' : ...,
                      'title' : ...,
                      'genres'  : [...],
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
                                    audios=Audio.objects.all(),
                                    onlyDownloadable=True)
    jsonString = simplejson.dumps(jsonStruct)
    return HttpResponse(jsonString, "application/json")

@login_required
def exporterexportall(request):
    jsonStruct = createExportStruct(movies=Movie.objects.all(),
                                    seasons=Season.objects.all(),
                                    audios=Audio.objects.all())
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

def createExportStruct(movies, seasons, audios, onlyDownloadable=False):
    jsonStruct = {}
    allItems = list(movies) + list(seasons) + list(audios)
    jsonStruct['movies'] = _jsonStructFromItemList(items=movies)
    jsonStruct['series'] = _jsonStructFromItemList(items=seasons)
    jsonStruct['audios'] = _jsonStructFromItemList(items=audios)
    jsonStruct['keys'] = _jsonStructKeys()
    jsonStruct['users'] = _jsonStructUser(allItems)
    return jsonStruct

def _jsonStructKeys(keyIdList=None):
    keysStruct = {}
    for key in EncryptionKey.objects.all():
        if not keyIdList or key.id in keyIdList:
            keysStruct[key.id] = {'chunkSize' : key.chunkSize,
                                  'key'       : key.key}
    return keysStruct

def _jsonStructUser(items):
    userStruct = {}
    for item in items:
        for itemInstance in ItemInstance.objects.filter(item=item):
            if itemInstance.creator and not itemInstance.creator.id in userStruct:
                userStruct[itemInstance.creator.id] = {'username' : itemInstance.creator.username,
                                                       'email'    : itemInstance.creator.email}
    return userStruct
