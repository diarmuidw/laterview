# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, QueryDict
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings
from django.contrib import messages


import pinax.apps.account


if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from django import forms
         
import datetime
import string
import random


from hmac import new
from hashlib import sha1
from base64 import encodestring

from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from twilio.twiml import Response

from django_twilio import settings
from django_twilio.decorators import twilio_view
from django_twilio.views import conference, dial, gather, play, record, say, \
        sms

    
import twitter
import logging



#import logging.handlers
logger = logging.getLogger(__name__)
#http_handler = logging.handlers.HTTPHandler(
#    '4r52.localtunnel.com:80',
#    '/log',
#    method='GET',
#)
#logger.addHandler(http_handler)

@twilio_view
def hello(request):
    """A simple test view that returns a HttpResponse object."""
    logger.debug("Calling hello")
    try:
        r = Response()

        with r.gather(numDigits=1, action=reverse("calls_gather"), method="GET") as g:
            g.say("""To hear your last tweet, press 1.
            Press 2 to record your message.
            Press any other key to start over.""")
        return r
    except Exception, ex:
        logger.debug(ex)
        return HttpResponse('<Response><Say>Error in Hello</Say></Response>', mimetype='text/xml')

@twilio_view
def gather(request):
    
    logger.debug("Calling gather")
    d = request.GET.get('Digits')
    logger.debug("Digit Pressed= %s" % d)
    try:
        r = Response()
        if d == "1":
            r.say('You pressed 1')
            try:
                api = twitter.Api()
                statuses = api.GetUserTimeline('diarmuid')
                
                r.say(statuses[0].text)
            except Exception, ex:
                logger.debug(ex)
                r.say("Error getting twitter results")
            r.redirect(reverse("calls_hello"))
            return r
        elif d == "2":
            r.say('You pressed 2')
            r.say("Record your message after the tone.")
            
            r.record(maxLength="10", action=reverse("calls_record"))
            return r
        else:
            return HttpResponseRedirect(reverse("calls_hello"))
    except Exception, ex:
        logger.debug(ex)
        return HttpResponse('<Response><Say>Error in Gather</Say></Response>', mimetype='text/xml')

        
    

@twilio_view
def record(request):
    """A simple test view that returns a HttpResponse object."""
    r = Response()
    try:
        
        u = request.POST['RecordingUrl']

        r.say("Thanks for the message... take a listen to your message .")
        r.play(u)
        r.say("Goodbye.")
        r.redirect(reverse("calls_hello"))
        return r
    except Exception, ex:
        logger.debug(ex)
        r.redirect(reverse("calls_hello"))
        
   
    return r
