from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^movies/', include('mediaExchange.movies.urls')),
    url(r'^queue/', include('mediaExchange.uploader.urls')),
    url(r'^users/', include('mediaExchange.users.urls')),
    url(r'^ajax/', include('mediaExchange.ajax.urls')),
    url(r'^items/', include('mediaExchange.items.urls')),
    url(r'^series/', include('mediaExchange.series.urls')),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':'/home/chriz/workspace/mediaExchange/mediaExchange/media', 'show_indexes':False}),
    url(r'^upload/', include('mediaExchange.mediaUpload.urls')),
    url(r'^about/', include('mediaExchange.about.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^.*', include('mediaExchange.index.urls'))
)
