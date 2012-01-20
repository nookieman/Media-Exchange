from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.movies.views',
    (r'^$', 'moviesindex'),
    (r'^details/(?P<movie_id>\d+)/?$', 'moviesdetails'),
    (r'^create/(?P<item_instance_id>\d+)/?$', 'moviescreate'),
    (r'^request/(?P<item_instance_id>\d+)/?$', 'moviesrequest'),
    (r'^addlinks/(?P<item_instance_id>\d+)/?$', 'moviesaddlinks'),
)

