from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFile
from mediaExchange.series.models import Season

@login_required
def indexindex(request):
#    items = Items.objects.all().order_by('-id')[:20]
    movies = Movie.objects.all().order_by('-id')[:20]
    seasons = Season.objects.all().order_by('-id')[:20]
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('index/index.html', {'movies':movies, 'seasons':seasons, 'uploadRequests':urs, 'doneUploadRequests':doneurs})
