from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import Item, UploadRequest

@login_required
def index(request):
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    return render_to_response('upload/index.html', { 'uploadRequests' : urs })
