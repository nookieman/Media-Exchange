from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.about.views',
    (r'^keyfile.txt$', 'getKeyFile'),
    (r'^.*$', 'aboutindex'),
)
