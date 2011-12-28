from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFile

@login_required
def indexindex(request):
    movies = Movie.objects.all().order_by('-id')[:20]
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('index/index.html', {'movies':movies, 'uploadRequests':urs, 'doneUploadRequests':doneurs})
