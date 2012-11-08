from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",

    url(r'^hello/$', 'calls.views.hello', name='calls_hello'),
    url(r'^gather/$', 'calls.views.gather', name='calls_gather'),
    url(r'^record/$', 'calls.views.record', name='calls_record'),


)
