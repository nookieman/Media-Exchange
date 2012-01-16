from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.exporter.views',
    (r'^all/$', 'exporterexportall'),
    (r'^downloadable/$', 'exporterexport'),
)
