from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import Item, Movie, UploadRequest, EncryptionKey
from mediaExchange.movies.views import moviesdetails
from mediaExchange.series.models import Season
from mediaExchange.series.views import seriesseasondetails
from mediaExchange.index.views import indexindex

@login_required
def itemsdetails(request, itemid):
    print 'itemsdetails(',itemid,')'
    item = get_object_or_404(Item, pk=itemid)
    if Movie.objects.filter(id=itemid):
        response = moviesdetails(request, itemid)
    elif Season.objects.filter(id=itemid):
        response = seriesseasondetails(request, itemid)
    else:
        response = indexindex(request)
    return response

@login_required
def itemsgetkey(request, keyid):
    print 'itemsgetkey', (keyid,)
    key = get_object_or_404(EncryptionKey, pk=keyid)
    keyfileContents = "%d\n%s" % (key.chunkSize, key.key)
    return HttpResponse(keyfileContents, content_type="text/plain")
