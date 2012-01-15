from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.series.views',
    (r'^$', 'seriesindex'),
    (r'^series/(?P<serie_id>\d+)/?$', 'seriesseriedetails'),
    (r'^season/(?P<season_id>\d+)/?$', 'seriesseasondetails'),
    (r'^create/(?P<season_id>\d+)/?$', 'seriesseasoncreate'),
    (r'^request/(?P<season_id>\d+)/?$', 'seriesseasonrequest'),
    (r'^addlinks/(?P<season_id>\d+)/?$', 'seriesseasonaddlinks'),
)
