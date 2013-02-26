from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",

    # new camera camera
    url(r'^$', 'upload.views.upload', name='upload_index'),
    #url(r'^upload/$', 'upload.views.upload', name='upload_index'),

)
