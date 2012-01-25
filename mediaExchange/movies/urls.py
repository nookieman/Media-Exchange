from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.movies.views',
    (r'^$', 'moviesindex'),
)

