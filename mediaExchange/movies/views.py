import os.path
import smtplib
from email.mime.text import MIMEText

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.movies.forms import AddItemUploadForm
from mediaExchange.movies.models import DownloadFile, DownloadFileGroup, EncryptionKey, ItemRequest, Movie, UploadRequest, Vote

@login_required
def moviesindex(request):
    movies = Movie.objects.all().order_by('name')
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('movies/index.html', {'movies':movies, 'uploadRequests':urs, 'doneUploadRequests':doneurs})

@login_required
def moviesdetails(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == 'POST':
        if 'watchable' in request.POST:
            v = Vote.objects.filter(user=request.user, movie=movie)
            watchable = request.POST['watchable'] == 'watchable'
            if not v:
                v = Vote(user=request.user, movie=movie, watchable=watchable)
            else:
                v = v[0]
                v.watchable = watchable
            v.save()
    return getDetails(request, movie)

@csrf_protect
@login_required
def moviescreate(request, movie_id):
    print 'create called'
    movie = get_object_or_404(Movie, pk=movie_id)
    if not DownloadFileGroup.objects.filter(item=movie):
        ur = UploadRequest.objects.filter(item=movie)
        if not ur:
            ur = UploadRequest(item=movie, user=request.user)
            ur.save()
    return getDetails(request, movie)

def getDetails(request, movie, message=None):
    c = {}

    sizeString = "Unknown"
    size = movie.size
    if size:
        s = (size, 'byte')
        if size > 1073741824:
            s = (round(size/1073741824.0, 2), 'GB')
        elif size > 1048576:
            s = (round(size/1048576.0, 2), 'MB')
        elif size > 1024:
            s = (round(size/1024.0, 2), 'KB')
        sizeString = "%.2f %s" % s
    downloadFileGroups = DownloadFileGroup.objects.filter(item=movie)
    ur = UploadRequest.objects.filter(item=movie)
    if ur:
        ur = ur[0]
    wvotes = Vote.objects.filter(movie=movie, watchable=True)
    nvotes = Vote.objects.filter(movie=movie, watchable=False)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    pathAvailable = movie.path != None and os.path.exists(movie.path)
    form = AddItemUploadForm()
    c.update(csrf(request))
    c.update({'movie'              : movie,
              'size'               : sizeString,
              'downloadFileGroups' : downloadFileGroups,
              'uploadRequest'      : ur,
              'wvotes'             : wvotes,
              'nvotes'             : nvotes,
              'uploadRequests'     : urs,
              'pathAvailable'      : pathAvailable,
              'message'            : message,
              'addItemForm'        : form})
    return render_to_response('movies/details.html', c)

@login_required
@csrf_protect
def moviesaddlinks(request, movie_id):
    c = {}
    movie = get_object_or_404(Movie, pk=movie_id)
    form = AddItemUploadForm(request.POST, request.FILES)
    msg = addLinks(item=movie, form=form)
    return getDetails(request, movie, msg)

def addLinks(item, form):
    msg = "Unable to add new links: Invalid form data."
    if form.is_valid():
        if form.cleaned_data['dlLinks'] or form.cleaned_data['dlLinksFile']:
            dlUrls = []
            if form.cleaned_data['dlLinks']:
                dlUrls = [ url.strip() for url in form.cleaned_data['dlLinks'].split(',')]
            else:
                dlUrls = [ url.strip() for url in form.cleaned_data['dlLinksFile'] ]
            if len(dlUrls) > 0:
                key = EncryptionKey.fromFileHandle(form.cleaned_data['keyfile'])
                downloadFileGroup = DownloadFileGroup(item=item, key=key)
                downloadFileGroup.save()
                for url in dlUrls:
                    df = DownloadFile(downloadFileGroup=downloadFileGroup, downloadLink=url)
                    df.save()
                msg = "Thanks for uploading new links."
            else:
                msg = "Unable to add new links: No download links found."
        else:
            msg = "Unable to add new links: Neither download links nor download links file given."
    return msg


@login_required
def moviesrequest(request, movie_id):
    c = {}
    movie = get_object_or_404(Movie, pk=movie_id)
    if movie.creator:
        msg = sendMovieRequestMail(movie, request.user)
        if not msg:
            ItemRequest(requester=request.user, item=movie).save()
            msg = "The contributor received a message of your request."
    else:
        msg = "Sorry the contributor of this item is unknown."
    return getDetails(request, movie, msg)

def sendMovieRequestMail(movie, requester):
    movietitle = "%s" % movie.name
    if movie.subname:
        movietitle += " - %s" % movie.subname
    subject = "Request for '%s' from '%s'" % (movietitle, str(requester))
    body = "%s has requested movie '%s'" % (movietitle, str(requester))
    if movie.source:
        body += "in %s" % movie.source.name
    return sendMail([movie.creator.email], subject, body)

def sendMail(rcpts, subject, body):
    sender = "mediaExchange@foobar.com"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(rcpts)
    try:
        server = smtplib.SMTP('localhost')
        server.sendmail(sender, rcpts, msg.as_string())
        server.quit()
    except Exception, e:
        return "Sorry, Unable to request item: '%s'" % str(e)
