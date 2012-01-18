from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.ajax.views',
    (r'^getstate/(?P<itemid>\d+)/?$', 'ajaxgetstate'),
    (r'^rate/?$', 'ajaxrate'),
)
