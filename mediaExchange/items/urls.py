from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.items.views',
    (r'^key/(?P<keyid>\d+)/$', 'itemsgetkey'),
    (r'^(?P<itemid>\d+)/$', 'itemsdetails'),
    (r'^create/(?P<item_instance_id>\d+)/?$', 'itemscreate'),
    (r'^request/(?P<item_instance_id>\d+)/?$', 'itemsrequest'),
    (r'^addlinks/(?P<item_instance_id>\d+)/?$', 'itemsaddlinks'),
)
