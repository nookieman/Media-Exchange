from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect

from mediaExchange.movies.forms import RatingForm
from mediaExchange.movies.models import Item, UploadRequest

import time

@login_required
def ajaxgetstate(request, itemid):
    item = get_object_or_404(Item, pk=itemid)
    ur = None
    if _statehaschanged(request, item):
        ur = UploadRequest.objects.filter(item=item)
        if ur:
            ur=ur[0]
    return render_to_response('ajax/getstate.html', {'uploadRequest':ur})

def _statehaschanged(request, item):
    result = True
    ur = UploadRequest.objects.filter(item=item)
    if ur:
        ur=ur[0]
    if not request.session.has_key('getstate'):
        request.session['getstate'] = {}
    if not request.session['getstate'].has_key(item.id):
        dict = {'state':ur.state}
        comp = 0
        if ur.state == 1:
            comp = ur.tared
        elif ur.state == 2:
            comp == ur.encrypted
        elif ur.state == 3:
            comp == ur.splitted
        elif ur.state == 4:
            comp = ur.uploaded
        dict.update({'value':comp})
        request.session['getstate'][item.id] = dict
    else:
        if request.session['getstate'][item.id]['state'] == ur.state:
            comp = 0
            if ur.state == 1:
                comp = ur.tared
            elif ur.state == 2:
                comp == ur.encrypted
            elif ur.state == 3:
                comp == ur.splitted
            elif ur.state == 4:
                comp = ur.uploaded
            if request.session['getstate'][item.id]['value'] == comp:
                result = False
    return result

@login_required
@csrf_protect
def ajaxrate(request):
    message = None
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['rating'] > 0 and form.cleaned_data['rating'] <= 10:
                rating = form.save(commit=False)
                rating.user = request.user
                rating.save()
                message = "Thanks for your rating."
            else:
                message = "Please use a rating between 1 and 10."
        else:
            message = "%s\nInvalid rating form:\n%s" % (str(request.POST), str(form.errors))
    else:
        message = "Missing POST parameters."
    return render_to_response('ajax/rate.html', {'message' : message})
