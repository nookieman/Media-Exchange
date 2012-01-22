from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, get_object_or_404

from mediaExchange.items.forms import AddItemUploadForm, RatingForm
from mediaExchange.items.models import DownloadFile, DownloadFileGroup, EncryptionKey, ItemInstance, ItemRequest, Rating, UploadRequest, Vote, Movie
from mediaExchange.items.views import sendMail

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
    return getMovieDetails(request, movie)

def getMovieDetails(request, item, message=None):
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
              'itemInstances'     : itemInstances,
              'wvotes'             : wvotes,
              'nvotes'             : nvotes,
              'uploadRequests'     : urs,
              'message'            : message,
              'addItemForm'        : form,
              'ratingForm'         : ratingForm})
    return render_to_response('movies/details.html', c)
