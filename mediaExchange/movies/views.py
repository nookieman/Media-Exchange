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

