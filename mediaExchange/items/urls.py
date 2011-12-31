from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.items.views',
    (r'^key/(?P<keyid>\d+)/$', 'itemsgetkey'),
    (r'^(?P<itemid>\d+)/$', 'itemsdetails'),
)
