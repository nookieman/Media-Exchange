from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.uploader.views',
    (r'^$', 'index'),
)
