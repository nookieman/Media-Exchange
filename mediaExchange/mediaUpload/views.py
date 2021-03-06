import os
import simplejson
import tarfile

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from mediaExchange.settings import MOVIE_SAVE_DIRECTORY
from mediaExchange.items.models import Language, Genre, Source, UploadRequest, EncryptionKey, DownloadFile, DownloadFileGroup, ItemInstance, Movie, Serie, Season, Artist, Audio
from mediaExchange.mediaUpload.forms import UploadForm, MovieUploadForm, SeriesUploadForm, AudioUploadForm, ItemInstanceForm, FileUploadForm, LinkUploadForm
from mediaExchange.mediaUpload.handlers import ProgressUploadHandler

@login_required
def mediaUploadindex(request):
    return render_to_response('mediaUpload/index.html', {})

@csrf_exempt
def mediaUpload(request, category):
    if not hasattr(request, '_post'):
        request.upload_handlers.insert(0, ProgressUploadHandler(request))
    return _mediaUpload(request, category)

@csrf_protect
@login_required
def _mediaUpload(request, category):
    c = {}
    error = None
    if request.method == 'POST':
        itemForm = UploadForm(request.POST, request.FILES)
        if itemForm.is_valid():
                itemForm, error = handleUpload(request, category)
        else:
            error = 'invalid UploadForm'
            itemForm = createForm(category)
    else:
        itemForm = createForm(category)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    itemInstanceForm = ItemInstanceForm()
    fileUploadForm = FileUploadForm()
    linkUploadForm = LinkUploadForm()
    c.update(csrf(request))
    c.update({'itemForm':itemForm, 'itemInstanceForm':itemInstanceForm,
              'linkUploadForm':linkUploadForm, 'fileUploadForm':fileUploadForm,
              'error':error, 'uploadRequests':urs})
    return render_to_response('mediaUpload/upload.html', c)

def handleUpload(request, category):
    error = None
    formClass = getFormClass(category)
    form = formClass(request.POST, request.FILES)
    if form.is_valid():
        try:
            itemClass = getItemClass(category)
            item = itemClass.handleForm(form)
            form, error = handleItemForm(request, form, item)
        except Language.DoesNotExist:#Exception, e:
            error = 'Having an error: %s' % str(e)
    else:
        error = 'invalid UploadForm'
    return form, error

def getFormClass(category):
    formClass = None
    if category == 'audio':
        formClass = AudioUploadForm
    elif category == 'movie':
        formClass = MovieUploadForm
    elif category == 'serie':
        formClass = SeriesUploadForm
    else:
        raise Exception("Invalid category '{0}'".format(category))
    return formClass

def createForm(category):
    formClass = getFormClass(category)
    return formClass()

def getItemClass(category):
    itemClass = None
    if category == 'audio':
        itemClass = Audio
    elif category == 'movie':
        itemClass = Movie
    elif category == 'serie':
        itemClass = Season
    else:
        raise Exception("Invalid category '%s'".format(category))
    return itemClass



def handleItemForm(request, form, item):
    error = None

    language = Language.getOrCreate(form.cleaned_data['language'])
    source = Source.getOrCreate(form.cleaned_data['source'])
    filesize = None
    if form.cleaned_data['size']:
        filesize = form.cleaned_data['size']

    itemInstance = ItemInstance.getOrCreate(size=filesize,
                                            language=language,
                                            source=source,
                                            creator=request.user,
                                            item=item)
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
