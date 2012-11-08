from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "docs/index.html"}, name="index"),
    url(r"^webcam$", direct_to_template, {"template": "docs/webcam.html"}, name="docs_webcam"),
    url(r"^petcam$", direct_to_template, {"template": "docs/petcam.html"}, name="docs_petcam"),
    url(r"^garagecam$", direct_to_template, {"template": "docs/garagecam.html"}, name="docs_garagecam"),
    url(r"^overview$", direct_to_template, {"template": "docs/overview.html"}, name="docs_overview"),
)
