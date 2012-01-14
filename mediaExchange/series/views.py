import os.path

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFileGroup, ItemRequest
from mediaExchange.movies.views import sendMail
from mediaExchange.series.models import Serie, Season


@login_required
def seriesindex(request):
    series = Serie.objects.all().order_by('name')
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    return render_to_response('series/index.html', {'series':series, 'uploadRequests':urs})

@login_required
def seriesseriedetails(request, serie_id):
    serie = get_object_or_404(Serie, pk=serie_id)
    return getSerieDetails(serie)

@login_required
def seriesseasondetails(request, season_id):
    season = get_object_or_404(Season, pk=season_id)
    return getSeasonDetails(request, season)

@login_required
def seriesseasoncreate(request, season_id):
    print 'create called'
    season = get_object_or_404(Season, pk=season_id)
    if not DownloadFileGroup.objects.filter(item=season):
        ur = UploadRequest.objects.filter(item=season)
        if not ur:
            ur = UploadRequest(item=season, user=request.user)
            ur.save()
    return getSeasonDetails(request, season)

def getSerieDetails(serie):
    seasons = Season.objects.filter(serie=serie)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('series/seriesdetails.html', {'serie':serie, 'seasons':seasons, 'uploadRequests':urs, 'doneUploadRequests':doneurs})

def getSeasonDetails(request, season, message=None):
    c = {}
    sizeString = "Unknown"
    size = season.size
    if size:
        s = (size, 'byte')
        if size > 1073741824:
            s = (round(size/1073741824.0, 2), 'GB')
        elif size > 1048576:
            s = (round(size/1048576.0, 2), 'MB')
        elif size > 1024:
            s = (round(size/1024.0, 2), 'KB')
        sizeString = "%.2f %s" % s
    downloadFileGroups = DownloadFileGroup.objects.filter(item=season)
    ur = UploadRequest.objects.filter(item=season)
    if ur:
        ur = ur[0]
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    pathAvailable = season.path != None and os.path.exists(season.path)
    c.update({'serie'              : season.serie,
              'season'             : season,
              'size'               : sizeString,
              'downloadFileGroups' : downloadFileGroups,
              'uploadRequest'      : ur,
              'uploadRequests'     : urs,
              'pathAvailable'      : pathAvailable,
              'message'            : message})
    c.update(csrf(request))
    return render_to_response('series/seasondetails.html', c)

@login_required
def seriesseasonrequest(request, season_id):
    c = {}
    season = get_object_or_404(Season, pk=season_id)
    if season.creator:
        msg = sendSeasonRequestMail(season, request.user)
        if not msg:
            itemRequest(requester=request.user, item=season).save()
            msg = "The contributor received a message of your request."
    else:
        msg = "Sorry the contributor of this item is unknown."
    return getSeasonDetails(request, season, msg)

def sendSeasonRequestMail(season, requester):
    subject = "Request for series '%s' season %d from '%s'" % (season.series.name,
                                                             season.number,
                                                             str(requester))
    body = "%s has request the series '%s' season %d" % (str(requester),
                                                         season.series.name,
                                                         season.number)
    if season.subname:
        body += " (%s)" % season.subname
    if season.source:
        body += "in %s" % season.source.name
    return sendMail([season.creator.mail], subject, body)
