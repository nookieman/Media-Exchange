import os.path

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.movies.forms import AddItemUploadForm
from mediaExchange.movies.models import UploadRequest, DownloadFileGroup, ItemRequest, ItemInstance
from mediaExchange.movies.views import addLinks, sendMail
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
def seriesseasoncreate(request, item_instance_id):
    print 'create called'
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if not DownloadFileGroup.objects.filter(itemInstance=itemInstance):
        ur = UploadRequest.objects.filter(itemInstance=itemInstance)
        if not ur:
            ur = UploadRequest(itemInstance=itemInstance, user=request.user)
            ur.save()
    return getSeasonDetails(request, itemInstance.item.getRealModel())

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

@login_required
def seriesseasonrequest(request, item_instance_id):
    c = {}
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if itemInstance.creator:
        msg = sendSeasonRequestMail(itemInstance, request.user)
        if not msg:
            itemRequest(requester=request.user, itemInstance=itemInstance).save()
            msg = "The contributor received a message of your request."
    else:
        msg = "Sorry the contributor of this item is unknown."
    return getSeasonDetails(request, itemInstance.item.getRealModel(), msg)

@login_required
@csrf_protect
def seriesseasonaddlinks(request, item_instance_id):
    c = {}
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    form = AddItemUploadForm(request.POST, request.FILES)
    msg = addLinks(itemInstance=itemInstance, form=form)
    return getSeasonDetails(request, itemInstance.item.getRealModel(), msg)

def sendSeasonRequestMail(itemInstance, requester):
    season = itemInstance.item.getRealModel()
    subject = "Request for series '%s' season %d from '%s'" % (season.series.name,
                                                             season.number,
                                                             str(requester))
    body = "%s has request the series '%s' season %d" % (str(requester),
                                                         season.series.name,
                                                         season.number)
    if season.subname:
        body += " (%s)" % season.subname
    if itemInstance.source:
        body += "in %s" % itemInstance.source.name
    return sendMail([itemInstance.creator.mail], subject, body)
