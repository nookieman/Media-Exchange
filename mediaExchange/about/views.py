from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response

from mediaExchange.movies.models import UploadRequest
from mediaExchange.settings import ENCRYPTION_KEY, ENCRYPTION_CHUNK_SIZE

@login_required
def aboutindex(request):
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    return render_to_response('about/index.html', {'uploadRequests':urs})

@login_required
def getKeyFile(request):
    keyfileContents = "%d\n%s" % (ENCRYPTION_CHUNK_SIZE, ENCRYPTION_KEY)
    return HttpResponse(keyfileContents, content_type="text/plain")

