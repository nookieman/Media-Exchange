from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.importer.views',
    (r'^$', 'importerimport'),
)
