from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.mediaUpload.views',
    (r'^progress/.*$', 'upload_progress'),
    (r'^.*$', 'mediaUploadindex'),
)
