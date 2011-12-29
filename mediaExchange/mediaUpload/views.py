import os
import simplejson
import tarfile

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError 
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from mediaExchange.settings import MOVIE_SAVE_DIRECTORY
from mediaExchange.movies.models import Movie, Language, MovieGenre, MovieSource, UploadRequest
from mediaExchange.series.models import Serie, Season, SerieGenre, SerieSource
from mediaExchange.mediaUpload.forms import UploadForm, MovieUploadForm, SeriesUploadForm
from mediaExchange.mediaUpload.handlers import ProgressUploadHandler

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
                path = generateDestinationPath(form)
                if form.cleaned_data['tar']:
                    tf = tarfile.open(fileobj=form.cleaned_data['file'])
                    tf.extractall(path=path)
                else:
                    destination = open(path+os.path.basename(form.cleaned_data['file'].name), 'wb+')
                    for chunk in form.cleaned_data['file'].chunks():
                        destination.write(chunk)
                    destination.close()
                filesize = form.cleaned_data['file'].size
                mtime = int(os.stat(path).st_mtime)

                language = None
                if form.cleaned_data['language']:
                    language = Language.objects.filter(name=form.cleaned_data['language'])
                    if language:
                        language = language[0]
                    else:
                        language = Language(name=form.cleaned_data['language'])
                        language.save()

                genre = None
                if form.cleaned_data['genre']:
                    genre = MovieGenre.objects.filter(name=form.cleaned_data['genre'])
                    if genre:
                        genre = genre[0]
                    else:
                        genre = MovieGenre(name=form.cleaned_data['genre'])
                        genre.save()

                source = None
                if form.cleaned_data['source']:
                    source = MovieSource.objects.filter(name=form.cleaned_data['source'])
                    if source:
                        source = source[0]
                    else:
                        source = MovieSource(name=form.cleaned_data['source'])
                        source.save()

                subname = None
                if form.cleaned_data['subname']:
                    subname = form.cleaned_data['subname']

                year = None
                if form.cleaned_data['year']:
                    year = form.cleaned_data['year']

                m = Movie(name=form.cleaned_data['name'], path=path, size=filesize,
                    mtime=mtime, subname=subname,
                    language=language, year=year,
                    genre=genre, source=source)
                m.save()
                form = None
                error = 'Thank you for contributing.'
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
        if not serieExists(form):
            createSerie(form.cleaned_data['name'])
        serie = Serie.objects.filter(name=form.cleaned_data['name'])[0]
        if not seasonExists(serie, form):
            try:
                path = generateDestinationPath(form)
                if form.cleaned_data['tar']:
                    tf = tarfile.open(fileobj=form.cleaned_data['file'])
                    tf.extractall(path=path)
                else:
                    destination = open(path+os.path.basename(form.cleaned_data['file'].name), 'wb+')
                    for chunk in form.cleaned_data['file'].chunks():
                        destination.write(chunk)
                    destination.close()
                filesize = form.cleaned_data['file'].size
                mtime = int(os.stat(path).st_mtime)

                language = None
                if form.cleaned_data['language']:
                    language = Language.objects.filter(name=form.cleaned_data['language'])
                    if language:
                        language = language[0]
                    else:
                        language = Language(name=form.cleaned_data['language'])
                        language.save()

                genre = None
                if form.cleaned_data['genre']:
                    genre = SerieGenre.objects.filter(name=form.cleaned_data['genre'])
                    if genre:
                        genre = genre[0]
                    else:
                        genre = SerieGenre(name=form.cleaned_data['genre'])
                        genre.save()

                source = None
                if form.cleaned_data['source']:
                    source = SerieSource.objects.filter(name=form.cleaned_data['source'])
                    if source:
                        source = source[0]
                    else:
                        source = SerieSource(name=form.cleaned_data['source'])
                        source.save()

                number = None
                if form.cleaned_data['number']:
                    number = form.cleaned_data['number']

                year = None
                if form.cleaned_data['year']:
                    year = form.cleaned_data['year']

                m = Season(serie=serie, number=number, path=path, size=filesize,
                           mtime=mtime, language=language, year=year,
                           genre=genre, source=source)
                m.save()
                form = None
                error = 'Thank you for contributing.'
            except Exception, e:
                error = 'Having an error: %s' % str(e)
        else:
            error = 'The movie already exists.'
    else:
        error = 'invalid MovieUploadForm'
    return form, error

def movieExists(form):
    result = False
    rms = Movie.objects.filter(name=form.cleaned_data['name'])
    for rm in rms:
        if form.cleaned_data['subname'] == rm.subname or (not form.cleaned_data['subname'] and not rm.subname):
            if form.cleaned_data['year'] == rm.year or (not form.cleaned_data['year'] and not rm.year):
                if form.cleaned_data['source'] == season.source or (not form.cleaned_data['source'] and not season.source):
                    if form.cleaned_data['language'] == rm.language or (not form.cleaned_data['language'] and not rm.language):
                        result = True
                        break
    return result

def serieExists(title):
    series = Serie.objects.filter(name=title)
    return len(series) > 0

def createSerie(title):
    serie = Serie(name=title)
    serie.save()
    return serie


def seasonExists(serie, form):
    result = False
    seasons = Season.objects.filter(serie=serie)
    for season in seasons:
        if form.cleaned_data['number'] == season.number:
            if form.cleaned_data['source'] == season.source or (not form.cleaned_data['source'] and not season.source):
                if form.cleaned_data['language'] == rm.language or (not form.cleaned_data['language'] and not rm.language):
                    result = True
                    break
    return result

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

