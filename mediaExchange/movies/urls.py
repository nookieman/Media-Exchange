from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.movies.views',
    (r'^$', 'moviesindex'),
    (r'^details/(?P<movie_id>\d+)/?$', 'moviesdetails'),
    (r'^create/(?P<movie_id>\d+)/?$', 'moviescreate'),
)

