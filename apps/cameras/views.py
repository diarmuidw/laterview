# Create your views here.


from django.shortcuts import render_to_response, get_object_or_404, redirect
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

from timezones import TIMEZONE_CHOICES

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from django import forms

from mongoengine import connect

import mongoobjects            
import datetime
import string
import random
import redis

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

class CameraForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #password = forms.CharField()
    description = forms.CharField(required=True)
    timezone = forms.CharField(required=True)

s3prefix = settings.S3PREFIX

@login_required
def add_camera(request):
    if request.method == 'POST': # If the form has been submitted...
        form = CameraForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
               
                a = pinax.apps.account.models.Account.objects.filter(user=request.user)
                camtzname = a[0].timezone.zone
            
                user = None
                users = mongoobjects.User.objects().filter(name=request.user.username)
                if users.count() == 0:
                  
                    try:
                        user = mongoobjects.User(email=request.user.email, name=u'' + request.user.username, password='12345')
                        user.save()
                    except Exception, ex:
                        print ex
                else:

                    user = users[0]

                timezone = form.cleaned_data['timezone']
                newtz = pytz.timezone(timezone)

                name = id_generator(6)
                password = id_generator(6)
<<<<<<< HEAD
               
                c = mongoobjects.Camera(owner=user, name='C_%s' % name, timezone=timezone, password='P_%s' % password,
                                         path='/tmp/t1/t2/t4/%s/' % 'C_%s' % name, perm='elradfmw' , description=form.cleaned_data['description'])
=======
                c = mongoobjects.Camera(owner = user, name = 'C_%s'%name, filter='none', timezone = timezone, password = 'P_%s'%password,
                                         path = '/tmp/t1/t2/t4/%s/'%'C_%s'%name, perm = 'elradfmw' , description = form.cleaned_data['description'] )
>>>>>>> f66efd8a8efbb351e543daa16891126f6a208004
                c.save()
                messages.add_message(request, messages.INFO,
                        u"Added new Camera - %s" % 'C_%s' % name
                        )
            except Exception, ex:
                messages.add_message(request, messages.ERROR,
                        u"Error adding new new Camera"
                        )
            return HttpResponseRedirect(reverse("camera_list_yours")) # Redirect after POST
    else:
        a = pinax.apps.account.models.Account.objects.filter(user=request.user)
        camtzname = a[0].timezone.zone
        form = CameraForm(initial={'timezone': camtzname}) # An unbound form
    
    return render_to_response('camera/camera_add.html', {
        'form': form, 'timezones': TIMEZONE_CHOICES
    }, context_instance=RequestContext(request))


@login_required
def your_cameras(request, template_name="camera/cameras.html"):
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
    cameras = []
    cams = []

    
    try:
        #Get the user's timezone
        a = pinax.apps.account.models.Account.objects.filter(user=request.user)
        camtzname = a[0].timezone
        #camtz = pytz.timezone(camtzname)
        #Say the cam has timezone 'US/Eastern'
        #
        utc = pytz.utc
        nowdt = datetime.datetime.utcnow()
        utcnow = utc.localize(nowdt)
        nowdt = camtzname.normalize(utcnow)
        
        
#        print nowdt
#        print utcnow
        hm = nowdt.strftime('%H/%M')
        dt = nowdt.strftime('%Y/%m/%d')
        fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        ch  = nowdt.strftime('%H')
        
#        
#        
#        camdt = camtzname.localize(nowdt)
#        print camdt
#        print camdt.strftime(fmt)
        
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0])
        for c in cams:
            cameras.append(c['name'])

    except Exception, ex:
        print ex

    return render_to_response(template_name, {
<<<<<<< HEAD
        "cameras": cams, "dt":dt, "s3prefix":s3prefix
        }, context_instance=RequestContext(request))
=======
        "cameras": cams,"dt":dt,
         "currenthour": ch,
          "s3prefix":s3prefix
          }, context_instance=RequestContext(request))
>>>>>>> f66efd8a8efbb351e543daa16891126f6a208004
    

@login_required
def your_camera_images(request, cam_id, year=0, month=0, day=0, hour=0, template_name="camera/camera_images.html"):
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
    images = []
    
    try:
        d = datetime.datetime(int(year),int(month),int(day),int(hour),0)
        minusone = datetime.timedelta(minutes =-60)
        plusone = datetime.timedelta(minutes =+60)
        
        dbefore = d+minusone
        dafter = d+plusone
        #2013/02/20/02/
        linkbefore = '%s/%02d/%02d/%02d'%(dbefore.year, dbefore.month, dbefore.day,dbefore.hour)
        linkafter = '%s/%02d/%02d/%02d'%(dafter.year, dafter.month, dafter.day,dafter.hour)

        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0], name=cam_id)

        camimages = mongoobjects.Image.objects().filter(camera=cams[0], day='%04d%02d%02d' % (int(year), int(month), int(day)), hour=hour)
        for i in camimages:
            images.append(i.key)
        
        try:
            data = "[['Hour','Number of Images']"
            print data
            r = redis.StrictRedis(host='localhost', port=6379, db=0)
            print r
            for i in range(0,24):
                rdata =  '%s~%s~%02d~%02d~%02d'%(cam_id,year,int(month), int(day), i)
                print rdata
                numimages = r.get(rdata)
                if numimages == None:
                    numimages = 0
                data = data + ",['%02d',%s]"%(i,numimages)
                
            data = data +"]"
            
            print data    
                
            
        except Exception, ex:
            print ex
            
    
   
        return render_to_response(template_name, {
            "camera": cams[0], "data":data, 'cam_id':cam_id, "images":camimages,"linkbefore":linkbefore, "linkafter":linkafter, 's3prefix':s3prefix
            }, context_instance=RequestContext(request))
    
    except Exception, ex:
        print ex
        return render_to_response("camera/noimage.html", {}, context_instance=RequestContext(request))
@login_required
<<<<<<< HEAD
def your_camera_data(request, cam_id, year=0, month=0, day=0, template_name="camera/camera_data.html"):
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
=======
def your_camera_data(request, cam_id, year = 0, month =0, day= 0, template_name="camera/camera_data.html"):
    connect (settings.MONGODATABASENAME,host=settings.MONGOHOST, port =settings.MONGOPORT, username=settings.MONGOUSERNAME, password = settings.MONGOPASSWORD)
>>>>>>> f66efd8a8efbb351e543daa16891126f6a208004
    data = []
    cdata = {}
    try:
        
        a = pinax.apps.account.models.Account.objects.filter(user=request.user)
        tz = a[0].timezone
        
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0], name=cam_id)

        hdata = {}
        camdata = mongoobjects.ImageData.objects().filter(camera=cams[0], year=year, month=month, day=day)
        for d in camdata:
            hdata[d.hour] = d.counts
       
        
        for i in range(0, 24):
            
            cdata = {}
            cdata['date'] = '%04d%02d%02d' % (int(year), int(month), int(day))
            cdata['hour'] = i
            try:
                cdata['counts'] = hdata[i]
                #get first image in hour
                try:
                    camimages = mongoobjects.Image.objects().filter(camera=cams[0], day='%04d%02d%02d' % (int(year), int(month), int(day)), hour=i)
                    cdata['firstimage'] = camimages[0].key
                except Exception , ex:
                    print "problem getting first image of hour"
                    cdata['firstimage'] = 'static/blank64x48.jpg'

            except:
                cdata['counts'] = 0
                cdata['firstimage'] = 'static/blank64x48.jpg'
            
            data.append(cdata)
        
                    
    except Exception, ex:
        print ex
    
    
    return render_to_response(template_name, {
        "camera": cams[0], "data":data, "year":year, "month":month, "day":day,
         "byear":year, "bmonth":month, "bday":int(day) - 1, "aday":int(day) + 1, 's3prefix':s3prefix
        }, context_instance=RequestContext(request))
    

@login_required
def camera_edit(request, cam_id, template_name="camera/edit/base.html"):

    return render_to_response(template_name, {
        'cam': cam_id,
    }, context_instance=RequestContext(request))
    
@login_required
def camera_security(request, cam_id, template_name="camera/edit/base.html"):

    return render_to_response(template_name, {
        'cam': cam_id,
    }, context_instance=RequestContext(request))



class CameraDescriptionForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #password = forms.CharField()
    description = forms.CharField(required=True)
    
    
@login_required
def camera_description(request, cam_id, template_name="camera/edit/description.html"):
    print cam_id
    user = None
    cam = None
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
    description = ''
    try:
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0], name=cam_id)
        cam = cams[0]
        description = cam.description
        
    except Exception, ex:
        print ex

    if request.method == 'POST': # If the form has been submitted...
        form = CameraDescriptionForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                description = form.cleaned_data['description']
                
                cam.description = description
                cam.save()
                        
     
                messages.add_message(request, messages.INFO,
                        u"Updated Camera Description to %s" % form.cleaned_data['description']
                        )
            except Exception, ex:
                messages.add_message(request, messages.ERROR,
                        u"There was a problem updating the description"
                        )
    else:
        #CameraFormSet = formset_factory(CameraDescriptionForm, extra=1)
        form = CameraDescriptionForm(initial={'description': description}) # An unbound form
    print 'aaaaaaaaaa'
    print description
    return render_to_response(template_name, {
        'form': form, 'cam': cam.name
    }, context_instance=RequestContext(request))

'''
Timezone form stuff

'''
import pytz

class CameraTimeZoneForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #timezone = forms.CharField()
    timezone = forms.CharField(required=True)
    
@login_required
def camera_timezone(request, cam_id, template_name="camera/edit/timezone.html"):


    user = None
    cam = None
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
    timezone = ''
    try:
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0], name=cam_id)
        cam = cams[0]
        originaltz = cam.timezone
        timezone = cam.timezone
        
    except Exception, ex:
        cam.timezone = 'UTC'

    if request.method == 'POST': # If the form has been submitted...
        form = CameraTimeZoneForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                timezone = form.cleaned_data['timezone']
                
                #check if it is a valid timezone

                newtz = pytz.timezone(timezone)
                
                cam.timezone = timezone
                cam.save()
                        
     
                messages.add_message(request, messages.INFO,
                        u"Updated Camera timezone to %s" % form.cleaned_data['timezone']
                        )
            except Exception, ex:
                messages.add_message(request, messages.ERROR,
                        u"There was a problem updating the timezone"
                        )
                timezone = originaltz
    else:
        #CameraFormSet = formset_factory(CameratimezoneForm, extra=1)
        form = CameraTimeZoneForm(initial={'timezone': timezone}) # An unbound form
    
    return render_to_response(template_name, {
        'form': form, 'cam': cam.name, 'timezones': cam.timezone
    }, context_instance=RequestContext(request))


'''
password form stuff
'''

class CameraPasswordForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #password = forms.CharField()
    password = forms.CharField(required=True)
    
@login_required
def camera_password(request, cam_id, template_name="camera/edit/password.html"):

    print cam_id
    user = None
    cam = None
    connect (settings.MONGODATABASENAME, host=settings.MONGOHOST, port=settings.MONGOPORT, username=settings.MONGOUSERNAME, password=settings.MONGOPASSWORD)
    password = ''
    try:
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner=user[0], name=cam_id)
        cam = cams[0]
        password = cam.password
        
    except Exception, ex:
        print ex

    if request.method == 'POST': # If the form has been submitted...
        form = CameraPasswordForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                password = form.cleaned_data['password']
                
                cam.password = password
                cam.save()
                        
     
                messages.add_message(request, messages.INFO,
                        u"Updated Camera password to %s" % form.cleaned_data['password']
                        )
            except Exception, ex:
                messages.add_message(request, messages.ERROR,
                        u"There was a problem updating the password"
                        )
    else:
        #CameraFormSet = formset_factory(CamerapasswordForm, extra=1)
        form = CameraPasswordForm(initial={'password': password}) # An unbound form
    print password
    return render_to_response(template_name, {
        'form': form, 'cam': cam.name, 'password': password
    }, context_instance=RequestContext(request))




'''
Camera filter
 '''
from django.forms.fields import DateField, ChoiceField, MultipleChoiceField
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Select, CheckboxInput
from django.forms.extras.widgets import SelectDateWidget


filters = (('none','No Filter'),('country.acv', 'Country'),
                            ('crossprocess.acv', 'Cross Process'),
                            ('desert.acv', 'Desert'),
                            ('forget.acv', 'Forget'),
                            ('Hefe.acv', 'Hefe'),
                            ('lumo.acv', 'lumo')
                            
                            
                            
                            )

class CameraFilterForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #timezone = forms.CharField()
    filter = forms.ChoiceField(required=False, widget=Select, choices=filters)
    
@login_required
def camera_filter(request, cam_id, template_name="camera/edit/filter.html"):


    user = None
    cam = None
    connect (settings.MONGODATABASENAME,host=settings.MONGOHOST, port =settings.MONGOPORT, username=settings.MONGOUSERNAME, password = settings.MONGOPASSWORD)
    filter = ''
    try:
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner = user[0], name = cam_id)
        cam = cams[0]
        originaltz =  cam.filter
        filter = cam.filter
        
    except Exception, ex:
        cam.filter = 'None'

    if request.method == 'POST': # If the form has been submitted...
        form = CameraFilterForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                filter = form.cleaned_data['filter']
                print filter
                #check if it is a valid filter
                cam.filter = filter
                cam.save()

                messages.add_message(request, messages.INFO,
                        u"Updated Camera filter" # to %s" %  form.cleaned_data['filter']
                        )
            except Exception, ex:
                print ex
                messages.add_message(request, messages.ERROR,
                        u"There was a problem updating the filter"
                        )
                
    else:
        #CameraFormSet = formset_factory(CamerafilterForm, extra=1)
        form = CameraFilterForm(initial={'filter': filter}) # An unbound form
    
    return render_to_response(template_name, {
        'form': form, 'cam': cam.name, 'filters': cam.filter
    },context_instance=RequestContext(request))



delchoices = (('delete','Delete'))

class CameraDeleteForm(forms.Form):
    #id = forms.CharField(max_length=100)
    #timezone = forms.CharField()
    #delete = forms.ChoiceField(required=True, widget=CheckboxInput, choices=delchoices)
    pass
    
@login_required
def camera_delete(request, cam_id, template_name="camera/edit/delete.html"):


    user = None
    cam = None
    connect (settings.MONGODATABASENAME,host=settings.MONGOHOST, port =settings.MONGOPORT, username=settings.MONGOUSERNAME, password = settings.MONGOPASSWORD)
    try:
        user = mongoobjects.User.objects().filter(name=request.user.username)
        cams = mongoobjects.Camera.objects().filter(owner = user[0], name = cam_id)
        cam = cams[0]    
   
        if request.method == 'POST': # If the form has been submitted...
            print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            form = CameraDeleteForm(request.POST) # A form bound to the POST data
            print 'bbbbbbbbbbbbbbbbbbbbbbbbbb'
            if form.is_valid(): # All validation rules pass
                try:
    
                    #delete = form.cleaned_data['delete']
                    #rint delete
                    #check if it is a valid filter
                    cam.delete()
    
                    messages.add_message(request, messages.INFO,
                            u"Camera Deleted" # to %s" %  form.cleaned_data['filter']
                            )
                except Exception, ex:
                    print ex
                    messages.add_message(request, messages.ERROR,
                            u"There was a problem deleting the camera"
                            )
                return redirect('camera_list_yours')
                   
        else:
            #CameraFormSet = formset_factory(CamerafilterForm, extra=1)
            form = CameraDeleteForm() # An unbound form
        
        return render_to_response(template_name, {
            'form': form, 'cam': cam.name, 'filters': 'aaa'
        },context_instance=RequestContext(request))
    except:
        messages.add_message(request, messages.ERROR,
                u"Mmmmmm. Something not right happened!"
                )
        return redirect('camera_list_yours')        
    
    
    
