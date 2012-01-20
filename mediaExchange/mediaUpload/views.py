import os
import simplejson
import tarfile

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from mediaExchange.settings import MOVIE_SAVE_DIRECTORY
from mediaExchange.movies.models import Movie, Language, Genre, Source, UploadRequest, EncryptionKey, DownloadFile, DownloadFileGroup, ItemInstance
from mediaExchange.series.models import Serie, Season
from mediaExchange.mediaUpload.forms import UploadForm, MovieUploadForm, SeriesUploadForm
from mediaExchange.mediaUpload.handlers import ProgressUploadHandler

@login_required
def mediaUploadindex(request):
    return render_to_response('mediaUpload/index.html', {})

@csrf_exempt
def mediaUploadMovie(request):
    if not hasattr(request, '_post'):
        request.upload_handlers.insert(0, ProgressUploadHandler(request))
    return _mediaUploadMovie(request)

@csrf_exempt
def mediaUploadSeries(request):
    if not hasattr(request, '_post'):
        request.upload_handlers.insert(0, ProgressUploadHandler(request))
    return _mediaUploadSeries(request)

@csrf_protect
@login_required
def _mediaUploadMovie(request):
    c = {}
    error = None
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
                form, error = handleMovie(request)
        else:
            error = 'invalid UploadForm'
            form = MovieUploadForm()
    else:
        form = MovieUploadForm()
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    c.update(csrf(request))
    c.update({'form':form, 'error':error, 'uploadRequests':urs})
    return render_to_response('mediaUpload/upload.html', c)

@csrf_protect
@login_required
def _mediaUploadSeries(request):
    c = {}
    error = None
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
                form, error = handleSerie(request)
        else:
            error = 'invalid UploadForm'
            form = SeriesUploadForm()
    else:
        form = SeriesUploadForm()
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    c.update(csrf(request))
    c.update({'form':form, 'error':error, 'uploadRequests':urs})
    return render_to_response('mediaUpload/upload.html', c)

def handleMovie(request):
    error = None
    form = MovieUploadForm(request.POST, request.FILES)
    if form.is_valid():
        if not movieExists(form):
            try:
                language = Language.getOrCreate(form.cleaned_data['language'])
                genre = Genre.getOrCreate(form.cleaned_data['genre'])
                source = Source.getOrCreate(form.cleaned_data['source'])

                subname = None
                if form.cleaned_data['subname']:
                    subname = form.cleaned_data['subname']

                year = None
                if form.cleaned_data['year']:
                    year = form.cleaned_data['year']

                filesize = None
                if form.cleaned_data['size']:
                    filesize = form.cleaned_data['size']

                m = Movie(name=form.cleaned_data['name'], size=filesize,
                          subname=subname, year=year, genre=genre)
                m.save()
                itemInstance = ItemInstance(size=filesize, language=language,
                                            source=source, present=False,
                                            creator=request.user, item=m)
                itemInstance.save()
                if form.cleaned_data['file']:
                    itemInstance.path = generateDestinationPath(form)
                    if form.cleaned_data['tar']:
                        tf = tarfile.open(fileobj=form.cleaned_data['file'])
                        tf.extractall(path=path)
                    else:
                        destination = open(path+os.path.basename(form.cleaned_data['file'].name), 'wb+')
                        for chunk in form.cleaned_data['file'].chunks():
                            destination.write(chunk)
                        destination.close()
                    itemInstance.size = form.cleaned_data['file'].size
                    itemInstance.mtime = int(os.stat(path).st_mtime)
                    itemInstance.present = True
                    itemInstance.save()
                    form = None
                    error = 'Thank you for contributing.'
                elif (form.cleaned_data['dlLinks'] or form.cleaned_data['dlLinksFile']) and form.cleaned_data['keyfile']:
                    dlUrls = []
                    if form.cleaned_data['dlLinks']:
                        dlUrls = [ url.strip() for url in form.cleaned_data['dlLinks'].split(',')]
                    else:
                        dlUrls = [ url.strip() for url in form.cleaned_data['dlLinksFile'] ]
                    if len(dlUrls) > 0:
                        key = EncryptionKey.fromFileHandle(form.cleaned_data['keyfile'])
                        downloadFileGroup = DownloadFileGroup(item=itemInstance, key=key)
                        downloadFileGroup.save()
                        for url in dlUrls:
                            df = DownloadFile(downloadFileGroup=downloadFileGroup, downloadLink=url)
                            df.save()
                    form = None
                    error = 'Thank you for contributing.'
                else:
                    form = None
                    error = "Thank you for enlisting your item. You will be contacted when someone requests this item."
            except Exception, e:
                error = 'Having an error: %s' % (e)
        else:
            error = 'The movie already exists.'
    else:
        error = 'invalid MovieUploadForm'
    return form, error

def handleSerie(request):
    error = None
    form = SeriesUploadForm(request.POST, request.FILES)
    if form.is_valid():
        serieCreated = False
        if not serieExists(form):
            createSerie(form.cleaned_data['name'])
            serieCreated = True
        serie = Serie.objects.filter(name=form.cleaned_data['name'])[0]
        if not seasonExists(serie, form):
            try:
                language = Language.getOrCreate(form.cleaned_data['language'])
                genre = Genre.getOrCreate(form.cleaned_data['genre'])
                source = Source.getOrCreate(form.cleaned_data['source'])

                number = None
                if form.cleaned_data['number']:
                    number = form.cleaned_data['number']

                subname = None
                if form.cleaned_data['subname']:
                    subname = form.cleaned_data['subname']

                year = None
                if form.cleaned_data['year']:
                    year = form.cleaned_data['year']

                filesize = None
                if form.cleaned_data['size']:
                    filesize = form.cleaned_data['size']

                season = Season.getOrCreate(serie=serie, size=filesize,
                                            subname=subname, number=number,
                                            language=language, year=year,
                                            genre=genre, source=source,
                                            present=False, creator=request.user)
                season.save()
                itemInstance = ItemInstance(size=filesize, language=language,
                                            source=source, present=False,
                                            creator=requests.user, item=season)
                itemInstance.save()

                if form.cleaned_data['file']:
                    itemInstance.path = generateDestinationPath(form)
                    if form.cleaned_data['tar']:
                        tf = tarfile.open(fileobj=form.cleaned_data['file'])
                        tf.extractall(path=path)
                    else:
                        destination = open(path+os.path.basename(form.cleaned_data['file'].name), 'wb+')
                        for chunk in form.cleaned_data['file'].chunks():
                            destination.write(chunk)
                        destination.close()
                    itemInstance.filesize = form.cleaned_data['file'].size
                    itemInstance.mtime = int(os.stat(path).st_mtime)
                    itemInstance.present = True
                    itemInstance.save()
                    form = None
                    error = 'Thank you for contributing.'
                elif (form.cleaned_data['dlLinks'] or form.cleaned_data['dlLinksFile']) and form.cleaned_data['keyfile']:
                    dlUrls = []
                    if form.cleaned_data['dlLinks']:
                        dlUrls = [ url.strip() for url in form.cleaned_data['dlLinks'].split(',')]
                    else:
                        dlUrls = [ url.strip() for url in form.cleaned_data['dlLinksFile'] ]
                    if len(dlUrls) > 0:
                        key = EncryptionKey.fromFileHandle(form.cleaned_data['keyfile'])
                        downloadFileGroup = DownloadFileGroup(itemInstance=itemInstance, key=key)
                        downloadFileGroup.save()
                        for url in dlUrls:
                            df = DownloadFile(downloadFileGroup=downloadFileGroup, downloadLink=url)
                            df.save()
                    form = None
                    error = 'Thank you for contributing.'
                else:
                    form = None
                    error = "Thank you for enlisting your item. You will be contacted when someone requests this item."
            except Exception, e:
                error = 'Having an error: %s' % str(e)
        else:
            error = 'The season already exists.'
    else:
        error = 'invalid SeriesUploadForm'
    return form, error


#TODO this has to be split for movies and series
def generateDestinationPath(form):
    result = "%s/%s" % (MOVIE_SAVE_DIRECTORY.rstrip('/'), form.cleaned_data['name'])
    if form.cleaned_data.has_key('subname') and form.cleaned_data['subname']:
        result += ' - %s' % form.cleaned_data['subname']
    if form.cleaned_data['year']:
        result += ' (%s)' % form.cleaned_data['year']
    result += '/'
    os.makedirs(result, 0777)
    return result

@login_required
def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    progress_id = ''
    if 'X-Progress-ID' in request.GET:
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        cache_key = "%s" % (progress_id)
        data = request.session.get('upload_progress_%s' % cache_key, None)
        return HttpResponse(simplejson.dumps(data))
    else:
        return HttpResponseServerError('Server Error: You must provide X-Progress-ID header or query param.')

