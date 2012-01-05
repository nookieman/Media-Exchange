import os.path

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf

from mediaExchange.movies.models import Movie, UploadRequest, DownloadFile, Vote

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

@login_required
def moviescreate(request, movie_id):
    print 'create called'
    movie = get_object_or_404(Movie, pk=movie_id)
    if not DownloadFile.objects.filter(item=movie):
        ur = UploadRequest.objects.filter(item=movie)
        if not ur:
            ur = UploadRequest(item=movie, user=request.user)
            ur.save()
    return getDetails(request, movie)

def getDetails(request, movie):
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
    downloadFiles = DownloadFile.objects.filter(item=movie)
    ur = UploadRequest.objects.filter(item=movie)
    if ur:
        ur = ur[0]
    wvotes = Vote.objects.filter(movie=movie, watchable=True)
    nvotes = Vote.objects.filter(movie=movie, watchable=False)
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    pathAvailable = movie.path != None and os.path.exists(movie.path)
    c.update(csrf(request))
    c.update({'movie'          : movie,
              'size'           : sizeString,
              'downloadFiles'  : downloadFiles,
              'uploadRequest'  : ur,
              'wvotes'         : wvotes,
              'nvotes'         : nvotes,
              'uploadRequests' : urs,
              'pathAvailable'  : pathAvailable})
    return render_to_response('movies/details.html', c)
