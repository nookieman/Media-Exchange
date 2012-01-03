from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFile
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
    return getSeasonDetails(season)

@login_required
def seriesseasoncreate(request, season_id):
    print 'create called'
    season = get_object_or_404(Season, pk=season_id)
    if not DownloadFile.objects.filter(item=season):
        ur = UploadRequest.objects.filter(item=season)
        if not ur:
            ur = UploadRequest(item=season, user=request.user)
            ur.save()
    return getSeasonDetails(season)

def getSerieDetails(serie):
    seasons = Season.objects.filter(serie=serie)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('series/seriesdetails.html', {'serie':serie, 'seasons':seasons, 'uploadRequests':urs, 'doneUploadRequests':doneurs})

def getSeasonDetails(season):
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
    downloadFiles = DownloadFile.objects.filter(item=season)
    ur = UploadRequest.objects.filter(item=season)
    if ur:
        ur = ur[0]
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    return render_to_response('series/seasondetails.html', {'serie':season.serie, 'season':season, 'size':sizeString, 'downloadFiles':downloadFiles, 'uploadRequest':ur, 'uploadRequests':urs})


