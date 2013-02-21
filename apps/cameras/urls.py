from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "camera/about.html"}, name="camera_about"),
    # your cameras
    url(r'^cameras/$', 'cameras.views.your_cameras', name='camera_list_yours'),

    # new camera camera
    url(r'^add/$', 'cameras.views.add_camera', name='camera_add'),

    url(r'^images/(?P<cam_id>\w+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/$', 'cameras.views.your_camera_images', name='your_camera_images'),
    
    url(r'^data/(?P<cam_id>\w+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'cameras.views.your_camera_data', name='your_camera_data'),
    # edit camera camera
    #url(r'^edit/(\d+)/$', 'cameras.views.camera_edit', name='camera_edit'),
    url(r"^graph/$", direct_to_template, {"template": "camera/graph.html"}, name="graph"),
    #destory camera camera
   ## url(r'^destroy/(\d+)/$', 'camera.views.destroy', name='camera_destroy'),
    url(r"^edit/(?P<cam_id>\w+)$", 'cameras.views.camera_edit', name="camera_edit"),
    url(r"^edit/description/(?P<cam_id>\w+)$", 'cameras.views.camera_description', name="camera_edit_description"),
    url(r"^edit/password/(?P<cam_id>\w+)$", 'cameras.views.camera_password', name="camera_edit_password"),
    url(r"^edit/timezone/(?P<cam_id>\w+)$", 'cameras.views.camera_timezone', name="camera_edit_timezone"),
    url(r"^edit/security/(?P<cam_id>\w+)$", 'cameras.views.camera_security', name="camera_edit_security"),
    url(r"^edit/filter/(?P<cam_id>\w+)$", 'cameras.views.camera_filter', name="camera_edit_filter"),
)
