import simplejson

from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect

from mediaExchange.importer.forms import ImportForm
from mediaExchange.items.models import Item, UploadRequest

@login_required
@csrf_protect
def importerimport(request):
    c = {}
    error = None
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                importDict = simplejson.load(form.cleaned_data['file'])
                Item.fromDict(importDict)
                error = "Successfully imported new items"
            except Exception, e:
                error = "Error while processing data: %s" % str(e)
            form = ImportForm()
        else:
            error = "Invalid Form"
    else:
        form = ImportForm()
    urs = UploadRequest.objects.filter(done=False).order_by('id')
    c.update(csrf(request))
    c.update({'form' : form, 'error' : error, 'uploadRequests' : urs})
    return render_to_response('importer/upload.html', c)
