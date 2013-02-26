from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, QueryDict, HttpResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from django import forms


import datetime
import string
import random

import logging
# Create your views here.
logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse ('works')

@csrf_exempt
def upload(request):
    if request.method == 'GET':
        logger.debug("GET")
        return HttpResponse( 'upload get')
    elif request.method == 'POST':
        logger.debug("POST")
        logger.debug(request.POST['data'])
        logger.debug(request.POST['id'])
        return HttpResponse( '')
    

    
      