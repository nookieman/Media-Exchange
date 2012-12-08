from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.audios.views',
    (r'^$', 'audiosindex'),
)

