from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import UploadRequest

@login_required
def aboutindex(request):
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    return render_to_response('about/index.html', {'uploadRequests':urs})
