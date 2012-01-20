import os.path
import smtplib
from email.mime.text import MIMEText

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.movies.forms import AddItemUploadForm, RatingForm
from mediaExchange.movies.models import DownloadFile, DownloadFileGroup, EncryptionKey, ItemInstance, ItemRequest, Movie, Rating, UploadRequest, Vote

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
def moviescreate(request, item_instance_id):
    print 'create called'
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if not DownloadFileGroup.objects.filter(itemInstance=itemInstance):
        ur = UploadRequest.objects.filter(itemInstance=itemInstance)
        if not ur:
            ur = UploadRequest(itemInstance=itemInstance, user=request.user)
            ur.save()
    return getDetails(request, movie)

def getDetails(request, item, message=None):
    c = {}

    item = item.getRealModel()
    wvotes = Vote.objects.filter(movie=item, watchable=True)
    nvotes = Vote.objects.filter(movie=item, watchable=False)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    form = AddItemUploadForm()
    ratingInitial = {'item':item}
    try:
        rating = Rating.objects.get(user=request.user, item=item)
        ratingInitial['rating'] = rating.rating
    except Rating.DoesNotExist:
        pass
    itemInstances = ItemInstance.objects.filter(item=item)
    ratingForm = RatingForm(initial=ratingInitial)
    c.update(csrf(request))
    c.update({'movie'              : item,
              'movieInstances'     : itemInstances,
              'wvotes'             : wvotes,
              'nvotes'             : nvotes,
              'uploadRequests'     : urs,
              'message'            : message,
              'addItemForm'        : form,
              'ratingForm'         : ratingForm})
    return render_to_response('movies/details.html', c)

@login_required
@csrf_protect
def moviesaddlinks(request, item_instance_id):
    c = {}
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    form = AddItemUploadForm(request.POST, request.FILES)
    msg = addLinks(itemInstance=itemInstance, form=form)
    return getDetails(request, itemInstance.item, msg)

def addLinks(itemInstance, form):
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
                downloadFileGroup = DownloadFileGroup(itemInstance=itemInstance, key=key)
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
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if movie.creator:
        msg = sendMovieRequestMail(movie, request.user)
        if not msg:
            ItemRequest(requester=request.user, itemInstance=item_instance_id).save()
            msg = "The contributor received a message of your request."
    else:
        msg = "Sorry the contributor of this item is unknown."
    return getDetails(request, itemInstance.item, msg)

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
