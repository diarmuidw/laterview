#from tastypie.resources import ModelResource
#from tastypie_mongoengine import resources
#from cameras.mongoobjects import Camera
#from django.conf import settings
##from mongoengine import connect
#
##import mongoengine
##connect (settings.MONGODATABASENAME,host=settings.MONGOHOST, port =settings.MONGOPORT, username=settings.MONGOUSERNAME, password = settings.MONGOPASSWORD)
#
#
#class CameraResource(resources.MongoEngineResource):
#    class Meta:
#        queryset = Camera.objects.all()
#        resource_name = 'camera'
#        
        
        
from tastypie.resources import ModelResource
from cameras.models import Camera


class CameraResource(ModelResource):
    class Meta:
        queryset = Camera.objects.all()
        resource_name = 'camera'
