from django.conf.urls.defaults import *

urlpatterns = patterns('mediaExchange.users.views',
    (r'^login/$', 'userslogin'),
    (r'^logout/$', 'userslogout'),
    (r'^registration/$', 'usersregistration'),
    (r'^confirmation/(?P<activation_key>[a-fA-F0-9]*)/$', 'usersconfirmation'),
)

