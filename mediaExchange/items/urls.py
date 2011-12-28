from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.items.views',
    (r'^(?P<itemid>\d+)/$', 'itemsdetails'),
)
