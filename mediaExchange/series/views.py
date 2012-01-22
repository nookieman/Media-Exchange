from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.items.forms import AddItemUploadForm
from mediaExchange.items.models import DownloadFileGroup, ItemInstance, ItemRequest, Serie, Season, UploadRequest
from mediaExchange.items.views import sendMail


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

def getSerieDetails(serie):
    seasons = Season.objects.filter(serie=serie)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('series/seriesdetails.html', {'serie':serie, 'seasons':seasons, 'uploadRequests':urs, 'doneUploadRequests':doneurs})

def getSeasonDetails(request, season, message=None):
    c = {}
    itemInstances = ItemInstance.objects.filter(item=season)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    form = AddItemUploadForm()
    c.update({'serie'              : season.serie,
              'season'             : season,
              'itemInstances'      : itemInstances,
              'uploadRequests'     : urs,
              'message'            : message,
              'addItemForm'        : form})
    c.update(csrf(request))
    return render_to_response('series/seasondetails.html', c)

