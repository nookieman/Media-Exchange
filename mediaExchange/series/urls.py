from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.series.views',
    (r'^$', 'seriesindex'),
    (r'^series/(?P<serie_id>\d+)/?$', 'seriesseriedetails'),
)
