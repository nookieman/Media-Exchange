from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.mediaUpload.views',
    (r'^progress/.*$', 'upload_progress'),
    (r'^movie/', 'mediaUploadMovie'),
    (r'^series/', 'mediaUploadSeries'),
    (r'^.*$', 'mediaUploadindex'),
)
