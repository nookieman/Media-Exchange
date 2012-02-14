import smtplib
from email.mime.text import MIMEText

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.items.forms import AddItemUploadForm, RatingForm
from mediaExchange.items.models import DownloadFile, DownloadFileGroup, Item, ItemInstance, ItemRequest, Rating, UploadRequest, EncryptionKey, Movie, Season, Vote
from mediaExchange.index.views import indexindex

@login_required
def itemsdetails(request, itemid):
    print 'itemsdetails(',itemid,')'
    item = get_object_or_404(Item, pk=itemid)

    if request.method == 'POST':
        if 'watchable' in request.POST:
            v = Vote.objects.filter(user=request.user, item=item)
            watchable = request.POST['watchable'] == 'watchable'
            if not v:
                v = Vote(user=request.user, item=item, watchable=watchable)
            else:
                v = v[0]
                v.watchable = watchable
            v.save()

    return getItemDetails(request, item)

@login_required
def itemsgetkey(request, keyid):
    print 'itemsgetkey', (keyid,)
    key = get_object_or_404(EncryptionKey, pk=keyid)
    keyfileContents = "%d\n%s" % (key.chunkSize, key.key)
    return HttpResponse(keyfileContents, content_type="text/plain")

@login_required
def itemscreate(request, item_instance_id):
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if not DownloadFileGroup.objects.filter(itemInstance=itemInstance):
        ur = UploadRequest.objects.filter(itemInstance=itemInstance)
        if not ur:
            ur = UploadRequest(itemInstance=itemInstance, user=request.user)
            ur.save()
    return getItemDetails(request, itemInstance.item)

@login_required
def itemsrequest(request, item_instance_id):
    c = {}
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    if itemInstance.creator:
        subject = itemInstance.getRequestMailSubject(request.user)
        body = itemInstance.getRequestMailBody(request.user)
        msg = sendMail([itemInstance.creator.email], subject, body)
        if not msg:
            ItemRequest(requester=request.user, itemInstance=itemInstance).save()
            msg = "The contributor received a message of your request."
    else:
        msg = "Sorry the contributor of this item is unknown."
    return getItemDetails(request, itemInstance.item, msg)

@login_required
@csrf_protect
def itemsaddlinks(request, item_instance_id):
    c = {}
    itemInstance = get_object_or_404(ItemInstance, pk=item_instance_id)
    form = AddItemUploadForm(request.POST, request.FILES)
    msg = addLinks(itemInstance=itemInstance, form=form)
    return getItemDetails(request, itemInstance.item, msg)

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

def getItemDetails(request, item, msg=None):
    c = {}
    item = item.getRealModel()
    itemInstances = ItemInstance.objects.filter(item=item)
    wvotes = Vote.objects.filter(item=item, watchable=True)
    nvotes = Vote.objects.filter(item=item, watchable=False)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    form = AddItemUploadForm()

    ratingInitial = {'item':item}
    try:
        rating = Rating.objects.get(user=request.user, item=item)
        ratingInitial['rating'] = rating.rating
    except Rating.DoesNotExist:
        pass
    ratingForm = RatingForm(initial=ratingInitial)

    c.update({'item'           : item,
              'itemInstances'  : itemInstances,
              'wvotes'         : wvotes,
              'nvotes'         : nvotes,
              'uploadRequests' : urs,
              'message'        : msg,
              'ratingForm'     : ratingForm,
              'addItemForm'    : form})
    c.update(csrf(request))
    return render_to_response('items/details.html', c)

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

