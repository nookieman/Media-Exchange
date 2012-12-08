from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from mediaExchange.items.models import UploadRequest, Audio

@login_required
def audiosindex(request):
    audios = Audio.objects.all().order_by('name')
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    doneurs = UploadRequest.objects.filter(done=True)
    return render_to_response('audios/index.html', {'audios':audios, 'uploadRequests':urs, 'doneUploadRequests':doneurs})

